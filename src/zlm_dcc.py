import socket

from zlm_settings import ZlmSettings


on_port_not_set = []
on_exception = []


def send_dcc_cmd(cmd):
    settings = ZlmSettings.instance()
    port = settings.get_current_dcc_port()
    if not port:
        for callback in on_port_not_set:
            callback(settings.current_dcc)
        return

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        command = bytes(cmd, 'utf-8')
        client.connect(('127.0.0.1', port))
        client.send(command)
    except Exception as e:
        for callback in on_exception:
            callback(e)
    finally:
        client.close()
