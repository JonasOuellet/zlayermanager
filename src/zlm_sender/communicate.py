from multiprocessing.connection import Client
from zlm_settings import ZlmSettings

KEY = 'secret'
ADDRESS = 'localhost'


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
            address = (ADDRESS, ZlmSettings.instance().communication_port)
            self._conn = Client(address, authkey=KEY)
            # conn.send(['openned'])
            return True
        except Exception as e:
            print(e)

        return False

    def close(self):
        if self._conn:
            self._conn.close()

        self._conn = None
