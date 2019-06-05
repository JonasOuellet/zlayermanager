import sys
import os

from PyQt5 import Qt, QtCore

import zlm_core
from zlm_settings import ZlmSettings

from zlm_ui import resources_rc
from zlm_ui.layer_widget import ZlmLayerWidget
from zlm_ui.comserver import CommunicationServer
from zlm_ui.settings_ui import SettingsDialog
from zlm_to_zbrush import import_base, import_layer
import zlm_dcc


class ZlmMainUI(Qt.QMainWindow):
    closing = QtCore.pyqtSignal()
    showing = QtCore.pyqtSignal()

    settings_changed = QtCore.pyqtSignal()

    default_settings = {
        'geometry': None
    }

    def __init__(self, file_path=None):
        Qt.QMainWindow.__init__(self)
        self.settings = ZlmSettings.instance().get('ui', self.default_settings)

        self.setWindowTitle("ZLayerManager")
        self._apply_custom_stylesheet()
        self.setWindowIcon(Qt.QIcon(':/zbrush.png'))
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)

        self.tw_widget = ZlmLayerWidget(self)
        self.lbl_subtool = Qt.QLabel("SubTool: ")

        self.lbl_layer_count = Qt.QLabel("0")

        pb_option = Qt.QPushButton(Qt.QIcon(':/gear.png'), '')
        pb_option.clicked.connect(self.show_option)

        topLayout = Qt.QHBoxLayout()
        topLayout.addWidget(self.lbl_subtool)
        topLayout.addStretch()
        topLayout.addWidget(self.lbl_layer_count, 0, Qt.Qt.AlignRight)
        topLayout.addWidget(Qt.QLabel("Layers"), 0, Qt.Qt.AlignRight)
        topLayout.addSpacing(20)
        topLayout.addWidget(pb_option)

        mainLayout = Qt.QVBoxLayout()

        mainLayout.addLayout(topLayout)
        mainLayout.addWidget(self.tw_widget)

        self.central_widget = Qt.QWidget()
        self.central_widget.setLayout(mainLayout)
        self.setCentralWidget(self.central_widget)

        zlm_dcc.on_exception.append(self.on_error)
        zlm_dcc.on_port_not_set.append(self.on_port_not_set)

        for i in range(3):
            zlm_core.main_layers.add_callback(i, self.update_layer_count)

        if file_path and os.path.exists(file_path):
            self.load_layers(file_path)

        geo = self.settings.get('geometry', None)
        if geo:
            self.setGeometry(*geo)

        # Setup the communication server
        self.com_server = CommunicationServer()
        self.com_server.add_callback('update', self.load_layers)
        self.com_server.add_callback('i_layer', import_layer)
        self.com_server.add_callback('i_base', import_base)
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
        zlm_core.main_layers.load_from_file(file_path)
        self.update_subtool_label()

    def update_subtool_label(self):
        subtool = zlm_core.main_layers.subtool
        if subtool:
            self.lbl_subtool.setText("SubTool: " + subtool.name)
        else:
            self.lbl_subtool.setText("SubTool: ")

    def _apply_custom_stylesheet(self):
        if getattr(sys, 'frozen', False):
            root = sys._MEIPASS
        else:
            root = os.path.dirname(__file__)

        stylesheet = os.path.join(root, 'stylesheet.css')
        try:
            with open(stylesheet, mode='r') as f:
                self.setStyleSheet(f.read())
        except:
            pass

    def show_option(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec():
            # check if communication port has changed if so restart
            # communication server
            if ZlmSettings.instance().communication_port != self.com_server._address[1]:
                self.com_server.restart()

            self.settings_changed.emit()

    def update_layer_count(self, *args, **kwargs):
        self.lbl_layer_count.setText(str(len(zlm_core.main_layers.instances_list)))

    def on_port_not_set(self, dcc):
        Qt.QMessageBox.warning(self, "Port not set", "Communication port not set. Please set it in the settings window.")

    def on_error(self, e):
        Qt.QMessageBox.warning(self, 'Could not communicate', 'Could not communicate with "{}".\n'
                                     'Please make sure port is opened.'.format(ZlmSettings.instance().current_dcc))
