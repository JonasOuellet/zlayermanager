import sys
import os
import tempfile
from multiprocessing.connection import Client


__all__ = [
    'send_command'
]


def _get_port_file():
    return os.path.join(tempfile.gettempdir(), '.zlmport')


def _get_port():
    try:
        with open(_get_port_file(), mode='r') as f:
            return int(f.read())
    except:
        raise Exception("Cannot find port.")


def send_command(cmd_name, *args):
    cmd_args = [cmd_name]
    cmd_args.extend(args)

    if sys.version_info > (3, 0):
        # need to use byte string
        client = Client(('localhost', _get_port()), authkey=b'secret')
    else:
        client = Client(('localhost', _get_port()), authkey='secret')
    client.send(cmd_args)
    client.close()
