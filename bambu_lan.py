"""Local (LAN mode) status polling for Bambu Lab printers.

Bambu Lab printers in LAN mode do not expose an HTTP status API. They speak
MQTTS on port 8883 (self-signed certificate — verification must be disabled,
the same approach used by every community Bambu LAN integration), authenticate
with username "bblp" and the printer's LAN access code as the password, and
push status as JSON on the `device/{serial}/report` topic. A `pushall`
request on `device/{serial}/request` prompts an immediate full status push
instead of waiting for the printer's own periodic report.
"""
import json
import ssl
import threading
import paho.mqtt.client as mqtt

MQTT_PORT = 8883


class BambuLANError(Exception):
    """Raised when a Bambu LAN printer can't be reached, authenticated, or
    doesn't respond with a status report in time."""
    pass


def get_bambu_lan_status(host, serial_number, access_code, timeout=8):
    """Connect to a Bambu Lab printer's local MQTT broker, request a full
    status push, and return the parsed `print` object from its report.

    Raises BambuLANError on connect failure, auth failure, or timeout.
    """
    report = {}
    got_report = threading.Event()
    connect_error = {}

    def on_connect(client, userdata, flags, reason_code, properties=None):
        if reason_code.is_failure:
            connect_error['message'] = f"MQTT connect failed: {reason_code}"
            got_report.set()
            return
        client.subscribe(f"device/{serial_number}/report")
        client.publish(
            f"device/{serial_number}/request",
            json.dumps({"pushing": {"sequence_id": "0", "command": "pushall"}})
        )

    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return
        if 'print' in payload:
            report.update(payload['print'])
            got_report.set()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"j3d-{serial_number}")
    client.username_pw_set('bblp', access_code)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(host, MQTT_PORT, keepalive=timeout)
    except Exception as e:
        raise BambuLANError(f"Could not connect to printer at {host}:{MQTT_PORT}: {e}")

    try:
        client.loop_start()
        received = got_report.wait(timeout=timeout)
    finally:
        client.loop_stop()
        client.disconnect()

    if connect_error:
        raise BambuLANError(connect_error['message'])
    if not received:
        raise BambuLANError("Printer did not respond within timeout — check the IP, access code, and that LAN mode is enabled")

    return report
