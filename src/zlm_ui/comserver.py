import time
from multiprocessing.connection import Listener, Client

from PyQt5.QtCore import QThread, QObject, pyqtSignal

from zlm_sender.communicate import set_port, delete_port


SECRET = bytes('secret', 'utf-8')


class CommunicationDeamon(QThread):
    commandReceived = pyqtSignal(object)

    def __init__(self, address):
        QThread.__init__(self)
        self.listener = Listener(address, authkey=SECRET)

    def run(self):
        while True:
            conn = self.listener.accept()
            self.connection = conn
            msg = conn.recv()
            if msg[0] == 'stop':
                self.listener.close()
                return

            conn.close()

            self.commandReceived.emit(msg)

    def get_port(self):
        return self.listener.address[1]

    def get_address(self):
        return self.listener.address


class CommunicationServer(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._deamon = None

        self._address = None
        self._command_dict = {}

    def isRunning(self):
        if not self._deamon:
            return False

        return self._deamon.isRunning()

    def start(self):
        if not self.isRunning():
            self._address = ('localhost', 0)
            self._deamon = CommunicationDeamon(self._address)
            # get the port and save it to setting file.
            self._address = self._deamon.get_address()
            set_port(self._address[1])

            self._deamon.commandReceived.connect(self._oncommand)
            self._deamon.start()
        else:
            raise Exception('Server already running')

    def stop(self):
        client = Client(self._address, authkey=SECRET)
        client.send(['stop'])
        client.close()

        delete_port()
        # wait for thread to finish
        while self._deamon.isRunning():
            time.sleep(0.001)

        self._deamon = None
        self._address = None

    def restart(self):
        if self._deamon:
            self.stop()
        self.start()

    def _oncommand(self, msg):
        func = self._command_dict.get(msg[0], None)
        if func:
            for f in func:
                f(*msg[1:])

    def add_callback(self, command_name, callback):
        if command_name not in self._command_dict:
            self._command_dict[command_name] = []

        self._command_dict[command_name].append(callback)

    def remove_callback(self, command_name, callback):
        try:
            self._command_dict[command_name].remove(callback)
        except Exception as e:
            print(e)
