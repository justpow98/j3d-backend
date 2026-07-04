from unittest.mock import patch

from models import db, Printer, PrinterConnection


def _make_bambu_lan_connection(user, api_url='http://192.168.1.50', serial_number='AC12345', access_code='abc123'):
    printer = Printer(user_id=user.id, name='Test Bambu', status='IDLE')
    db.session.add(printer)
    db.session.flush()
    connection = PrinterConnection(
        printer_id=printer.id,
        user_id=user.id,
        connection_type='bambu_lan',
        api_url=api_url,
        serial_number=serial_number,
        access_code=access_code,
    )
    db.session.add(connection)
    db.session.commit()
    return connection


def test_status_endpoint_returns_parsed_bambu_data(client, user):
    u, token = user
    connection = _make_bambu_lan_connection(u)

    fake_print_info = {
        'gcode_state': 'RUNNING',
        'mc_percent': 55,
        'layer_num': 10,
        'total_layer_num': 200,
        'bed_temper': 60.0,
        'nozzle_temper': 220.0,
        'chamber_temper': 35.0,
        'print_error': 0,
    }

    with patch('app.get_bambu_lan_status', return_value=fake_print_info) as mock_status:
        resp = client.get(
            f'/api/printer-connections/{connection.id}/status',
            headers={'Authorization': f'Bearer {token}'}
        )

    assert resp.status_code == 200
    body = resp.get_json()
    assert body['connection_status'] == 'connected'
    assert body['status'] == {
        'state': 'RUNNING',
        'progress': 55,
        'current_layer': 10,
        'total_layers': 200,
        'bed_temp': 60.0,
        'nozzle_temp': 220.0,
        'chamber_temp': 35.0,
        'print_error': 0,
    }
    # Hostname extracted from the stored api_url (not the raw "http://..." string)
    mock_status.assert_called_once_with('192.168.1.50', 'AC12345', 'abc123')


def test_status_endpoint_returns_502_on_bambu_lan_error(client, user):
    from bambu_lan import BambuLANError

    u, token = user
    connection = _make_bambu_lan_connection(u)

    with patch('app.get_bambu_lan_status', side_effect=BambuLANError('Printer did not respond within timeout')):
        resp = client.get(
            f'/api/printer-connections/{connection.id}/status',
            headers={'Authorization': f'Bearer {token}'}
        )

    assert resp.status_code == 502
    body = resp.get_json()
    assert 'did not respond' in body['error']
    assert body['connection_status'] == 'error'

    db.session.refresh(connection)
    assert connection.status == 'error'


def test_status_endpoint_requires_serial_and_access_code(client, user):
    u, token = user
    connection = _make_bambu_lan_connection(u, serial_number=None, access_code=None)

    resp = client.get(
        f'/api/printer-connections/{connection.id}/status',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert resp.status_code == 400
    assert 'Serial number' in resp.get_json()['error']
