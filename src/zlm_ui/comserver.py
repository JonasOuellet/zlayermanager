from PySide2.QtCore import QThread, QObject
from zlm_settings import ZlmSettings
from multiprocessing.connection import Listener, Client
import time


class CommunicationDeamon(QThread):
    commandReceived = Signal(object)

    def __init__(self, address, secret):
        QThread.__init__(self)
        self.batcherUI = batcherUI
        self.listener = Listener(address, authkey=secret)
        self.connection = None

    def run(self):
        while True:
            conn = self.listener.accept()
            self.connection = conn
            msg = conn.recv()
            if msg[0] == 'stop':
                self.listener.close()
                return

            self.commandReceived.emit(msg)

            while self.connection:
                self.msleep(10)


class CommunicationServer(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._deamon = None
        self.settings = ZlmSettings.instance()

        self._address = None
        self._secret = 'secret'

        self._command_dict = {}

    def isRunning(self):
        if not self._deamon:
            return False

        return self._deamon.isRunning()

    def start(self):
        if not self.isRunning():
            self._address = ('localhost', self.settings.communication_port)
            self._deamon = CommunicationDeamon(self._address, self._secret)
            self._deamon.commandReceived.connect(self._oncommand)
            self._deamon.start()
        else:
            raise Exception('Server already running')

    def stop(self):
        client = Client(self._address, authkey=self._secret)
        client.send(['stop'])
        client.close()

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
        func = self._command_dict(msg[0], None)
        if func:
            for f in func:
                f(msg)

    def add_callback(self, command_name, callback):
        if command_name not in self._command_dict:
            self._command_dict[command_name] = []

        self._command_dict[command_name].append(callback)

    def remove_callback(self, command_name, callback):
        try:
            self._command_dict[command_name].remove(callback)
        except Exception as e:
            print(e)
