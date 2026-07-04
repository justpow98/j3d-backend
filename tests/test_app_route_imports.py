"""Route-level smoke tests for app.py's Etsy/Manyfold endpoints.

These exist because a bad merge once left ListingSyncManager and the whole
manyfold_api module used in app.py but never imported — every unit test for
ListingSyncManager/ManyfoldAPI themselves still passed (they import those
directly), so nothing caught it until it hit production as a NameError.
Hitting the actual routes, with only the network-facing calls mocked,
exercises the same name resolution Python does at request time.
"""
from unittest.mock import patch

from models import db, ManyfoldSettings


def test_sync_products_route_resolves_listing_sync_manager(client, user, token):
    with patch('app._ensure_etsy_access', return_value=(object(), 'shop1')), \
         patch('app.ListingSyncManager') as mock_manager:
        mock_manager.sync_listings_from_etsy.return_value = {'success': True, 'message': 'ok'}
        resp = client.post(
            '/api/products/sync-etsy',
            headers={'Authorization': f'Bearer {token}'}
        )

    assert resp.status_code == 200
    assert resp.get_json()['success'] is True


def test_manyfold_models_route_resolves_manyfold_api(client, user, token):
    settings = ManyfoldSettings(
        user_id=user.id,
        base_url='https://manyfold.example.com',
        client_id='cid',
        client_secret='secret',
    )
    db.session.add(settings)
    db.session.commit()

    with patch('app.ManyfoldAPI') as mock_api_cls:
        mock_api_cls.return_value.list_models.return_value = {'totalItems': 0, 'member': []}
        resp = client.get(
            '/api/integrations/manyfold/models',
            headers={'Authorization': f'Bearer {token}'}
        )

    assert resp.status_code == 200
    assert resp.get_json() == {'totalItems': 0, 'member': []}
