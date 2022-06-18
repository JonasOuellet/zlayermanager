import sys
import os
import webbrowser

from PyQt5 import QtWidgets, QtCore, QtGui

import zlm_core
from zlm_settings import ZlmSettings

from zlm_ui import resources_rc
from zlm_ui.layer_widget import ZlmLayerWidget
from zlm_ui.comserver import CommunicationServer
from zlm_ui.settings_ui import SettingsDialog
from zlm_ui.reorder_layer import ReorderLayerUI
from zlm_ui.rename_dialog import RenameDialog
from zlm_ui.process_info import ProcesInfo
from zlm_to_zbrush import (
    import_base,
    import_layer,
    send_new_layer_order,
    send_to_zbrush,
    send_update_request,
    send_new_layers_name
)
import zlm_app
import version


class VersionThread(QtCore.QThread):
    completed = QtCore.pyqtSignal(bool)

    def run(self):
        self.sleep(1)
        valid = True
        try:
            valid = version.is_version_valid()
        except:
            pass

        self.completed.emit(valid)


class VersionDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle("New version available")

        self.cb_check_for_update = QtWidgets.QPushButton("Always check for updates.")
        self.cb_check_for_update.setCheckable(True)
        self.cb_check_for_update.setChecked(ZlmSettings.instance().check_for_updates)

        pb_download = QtWidgets.QPushButton("Download")
        pb_download.clicked.connect(self.accept)

        pb_cancel = QtWidgets.QPushButton("Cancel")
        pb_cancel.clicked.connect(self.reject)

        label = QtWidgets.QLabel("A new version is available. Would you like to download it?")
        label.setWordWrap(True)

        layout = QtWidgets.QGridLayout()

        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(self.cb_check_for_update, 1, 0, 1, 2)
        layout.addItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed), 2, 0, 1, 2)
        layout.addWidget(pb_download, 3, 0, 1, 1)
        layout.addWidget(pb_cancel, 3, 1, 1, 1)

        self.setLayout(layout)

    def stop_looking_for_update(self):
        return not self.cb_check_for_update.isChecked()


class ZlmMainUI(QtWidgets.QMainWindow):
    closing = QtCore.pyqtSignal()
    showing = QtCore.pyqtSignal()

    settings_changed = QtCore.pyqtSignal()

    default_settings = {
        'geometry': None,
        'always_on_top': False
    }

    def __init__(self, file_path=None):
        QtWidgets.QMainWindow.__init__(self)
        self.settings = ZlmSettings.instance().get('ui', self.default_settings)

        self.setWindowTitle("ZLayerManager v{}".format(version.current_version))
        self._apply_custom_stylesheet()
        self.setWindowIcon(QtGui.QIcon(':/zbrush.png'))

        # Qt.Qt.WindowFlags
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, self.settings.get("always_on_top", False))

        self.tw_widget = ZlmLayerWidget(self)
        self.lbl_subtool = QtWidgets.QLabel("SubTool: ")

        self.lbl_layer_count = QtWidgets.QLabel("0")

        pb_option = QtWidgets.QPushButton(QtGui.QIcon(':/gear.png'), '')
        pb_option.clicked.connect(self.show_option)

        pb_help = QtWidgets.QPushButton(QtGui.QIcon(':/help.png'), '')
        pb_help.clicked.connect(self.open_help_url)

        topLayout = QtWidgets.QHBoxLayout()
        topLayout.addWidget(self.lbl_subtool)
        topLayout.addStretch()
        topLayout.addWidget(self.lbl_layer_count, 0, QtCore.Qt.AlignRight)
        topLayout.addWidget(QtWidgets.QLabel("Layers"), 0, QtCore.Qt.AlignRight)
        topLayout.addSpacing(20)
        topLayout.addWidget(pb_option)
        topLayout.addWidget(pb_help)

        mainLayout = QtWidgets.QVBoxLayout()

        mainLayout.addLayout(topLayout)
        mainLayout.addWidget(self.tw_widget)

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(mainLayout)
        self.setCentralWidget(self.central_widget)

        # creating menu
        menuBar = self.menuBar()
        menu = menuBar.addMenu("Edit")
        action = menu.addAction("Reorder Layers")
        action.triggered.connect(self.open_reorder_layer)

        fix_layer_name = menu.addAction(QtGui.QIcon(':/rename.png'), "Remove name duplicate")
        fix_layer_name.triggered.connect(self.remove_name_dup)

        bulk_rename = menu.addAction(QtGui.QIcon(':/rename.png'), "Rename all")
        bulk_rename.triggered.connect(self.bulk_rename)

        zlm_app.on_exception.append(self.on_error)
        zlm_app.on_port_not_set.append(self.on_port_not_set)

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
        self.com_server.add_callback('update_from_zbrush', send_update_request)
        self.com_server.add_callback('update_zbrush', send_to_zbrush)
        self.com_server.start()

        self._firstTime = True
        self._version_thread = None

    def showEvent(self, event):
        self.showing.emit()

        if self._firstTime:
            self._firstTime = False

            if ZlmSettings.instance().check_for_updates:
                self.check_for_updates()

    def check_for_updates(self):
        if self._version_thread is None:
            self._version_thread = VersionThread()
            self._version_thread.completed.connect(self.on_valid_version)
            self._version_thread.start()

    def on_valid_version(self, valid):
        if not valid:
            dialog = VersionDialog(self)
            if dialog.exec_():
                try:
                    webbrowser.open("https://jonasouellet.github.io/zlayermanager/installation.html")
                except:
                    pass

            if dialog.stop_looking_for_update():
                ZlmSettings.instance().check_for_updates = False

        self._version_thread = None

    def closeEvent(self, event):
        if self._version_thread and self._version_thread.isRunning():
            self._version_thread.terminate()
            self._version_thread.wait()

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
        was_check_updates = ZlmSettings.instance().check_for_updates
        if settings_dialog.exec():
            always_on_top = self.settings.get("always_on_top", False)
            flags = self.windowFlags()
            on_top = flags & QtCore.Qt.WindowStaysOnTopHint == QtCore.Qt.WindowStaysOnTopHint
            if on_top != always_on_top:
                self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, always_on_top)
                self.show()

            if not was_check_updates and ZlmSettings.instance().check_for_updates:
                self.check_for_updates()

            self.settings_changed.emit()

    def open_help_url(self):
        try:
            webbrowser.open("https://jonasouellet.github.io/zlayermanager/userguide/index.html")
        except:
            pass

    def update_layer_count(self, *args, **kwargs):
        self.lbl_layer_count.setText(str(len(zlm_core.main_layers.instances_list)))

    def on_port_not_set(self, app):
        QtWidgets.QMessageBox.warning(
            self,
            "Port not set",
            "Communication port not set. Please set it in the settings window."
        )

    def on_error(self, e):
        QtWidgets.QMessageBox.warning(
            self,
            'Could not communicate',
            'Could not communicate with "{}".\n'
            'Please make sure port is opened.'.format(ZlmSettings.instance().current_app)
        )

    def open_reorder_layer(self):
        inst = ReorderLayerUI(self)
        geo = self.settings.get("reorderWindowGeo", None)
        if geo:
            try:
                inst.setGeometry(*geo)
            except:
                pass
        if inst.exec_():
            # update layer
            layers = inst.get_layers()
            window = ProcesInfo(self, "Updating zbrush.  Please wait...")
            window.show()
            QtWidgets.QApplication.processEvents()
            send_new_layer_order(layers)
            window.close()

        geo = inst.geometry()
        self.settings['reorderWindowGeo'] = [geo.x(), geo.y(), geo.width(), geo.height()]

    def remove_name_dup(self):
        layers = zlm_core.main_layers.fix_up_names()
        if layers:
            send_new_layers_name(layers)

    def bulk_rename(self):
        if zlm_core.main_layers.instances_list:
            _, ex_name = zlm_core.main_layers.remove_invalid_char(zlm_core.main_layers.instances_list[0].name)
        else:
            ex_name = "layerName"
        dialog = RenameDialog(ex_name, self)
        if dialog.exec_():
            names = [layer.name for layer in zlm_core.main_layers.instances_list]
            new_names = dialog.rename(names)
            mod_layers = []
            for layer, new_name in zip(zlm_core.main_layers.instances_list, new_names):
                if zlm_core.main_layers.rename_layer(layer, new_name):
                    mod_layers.append(layer)

            if mod_layers:
                send_new_layers_name(mod_layers)
