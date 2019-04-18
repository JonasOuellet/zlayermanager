import sys
import os

from PySide2 import QtWidgets, QtCore, QtGui

import zlm_core
from zlm_settings import ZlmSettings
from zlm_ui.layer_widget import ZlmLayerWidget
from zlm_ui.comserver import CommunicationServer

from zlm_ui import resources_rc


class ZlmMainUI(QtWidgets.QMainWindow):
    closing = QtCore.Signal()
    showing = QtCore.Signal()

    default_settings = {
        'geometry': None
    }

    def __init__(self, file_path=None):
        QtWidgets.QMainWindow.__init__(self)
        self.settings = ZlmSettings.instance().get('ui', self.default_settings)

        self.setWindowTitle("ZLayerManager")
        self._apply_custom_stylesheet()
        self.setWindowIcon(QtGui.QIcon(':/zbrush.png'))
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)

        self.tw_widget = ZlmLayerWidget(self)
        self.lbl_subtool = QtWidgets.QLabel("SubTool: ")

        mainLayout = QtWidgets.QVBoxLayout()

        mainLayout.addWidget(self.lbl_subtool)
        mainLayout.addWidget(self.tw_widget)

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(mainLayout)
        self.setCentralWidget(self.central_widget)

        self.layers = None
        self.subTool = None

        if file_path:
            self.load_layers(file_path)

        geo = self.settings.get('geometry', None)
        if geo:
            self.setGeometry(*geo)

        # Setup the communication server
        self.com_server = CommunicationServer()
        self.com_server.add_callback('update', self.load_layers)
        self.com_server.start()

    def showEvent(self, event):
        self.showing.emit()

    def closeEvent(self, event):
        self.com_server.stop()
        self.closing.emit()

        geo = self.geometry()
        self.settings['geometry'] = [geo.x(), geo.y(), geo.width(), geo.height()]

        ZlmSettings.instance().save_to_file()

    def load_layers(self, file_path):
        self.layers, self.subTool = zlm_core.parse_layer_file(file_path)
        self.tw_widget.build()
        self.update_subtool_label()

    def update_subtool_label(self):
        if self.subTool:
            self.lbl_subtool.setText("SubTool: " + self.subTool.name)
        else:
            self.lbl_subtool.setText("SubTool: ")

    def _apply_custom_stylesheet(self):
        if getattr(sys, 'frozen', False):
            root = sys.executable
        else:
            root = __file__

        stylesheet = os.path.join(os.path.dirname(root), 'stylesheet.css')
        try:
            with open(stylesheet, mode='r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(e)
