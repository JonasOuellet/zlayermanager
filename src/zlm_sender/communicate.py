from multiprocessing.connection import Client
import tempfile
import os


KEY = bytes('secret', 'utf-8')
ADDRESS = 'localhost'


def get_port_file():
    return os.path.join(tempfile.gettempdir(), '.zlmport')


def get_port():
    try:
        with open(get_port_file(), mode='r') as f:
            return int(f.read())
    except:
        pass

    return None


def set_port(port):
    with open(get_port_file(), mode='w') as f:
        f.write(str(port))


def delete_port():
    try:
        os.remove(get_port_file())
    except:
        pass


class Connection(object):
    def __init__(self):
        self._conn = None

    def __enter__(self):
        if self.connect():
            return self._conn
        else:
            return None

    def __exit__(self, type, value, traceback):
        self.close()

    def connect(self):
        try:
            port = get_port()
            if port is not None:
                address = (ADDRESS, port)
                self._conn = Client(address, authkey=KEY)
                return True
        except Exception as e:
            print(e)

        return False

    def close(self):
        if self._conn:
            self._conn.close()

        self._conn = None

    def send(self, *args):
        try:
            self._conn.send(args)
        except:
            pass
