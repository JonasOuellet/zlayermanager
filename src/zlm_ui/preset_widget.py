from PyQt5 import Qt, QtCore

import zlm_core
from zlm_ui.collapsable import ZlmCollapsableWidget


class ZlmPresetWidget(ZlmCollapsableWidget):
    preset_activated = QtCore.pyqtSignal()

    def __init__(self):
        ZlmCollapsableWidget.__init__(self, "Presets: ")

        self.cb_preset_file = Qt.QComboBox()
        self.cb_layer_presets = Qt.QComboBox()
        self.pb_activate = Qt.QPushButton('Activate')
        self.pb_activate.clicked.connect(self.on_preset_activated)

        self.pb_add_file = Qt.QPushButton(Qt.QIcon(':/add.png'), '')
        self.pb_add_file.pressed.connect(self.pb_add_file_pressed)
        self.pb_rem_file = Qt.QPushButton(Qt.QIcon(':/remove.png'), '')
        self.pb_rem_file.pressed.connect(self.pb_rem_file_pressed)

        self.pb_add_preset = Qt.QPushButton(Qt.QIcon(':/add.png'), '')
        self.pb_add_preset.pressed.connect(self.pb_add_preset_pressed)
        self.pb_rem_preset = Qt.QPushButton(Qt.QIcon(':/remove.png'), '')
        self.pb_rem_preset.pressed.connect(self.pb_rem_preset_pressed)
        self.pb_save_preset = Qt.QPushButton(Qt.QIcon(':/save.png'), '')
        self.pb_save_preset.pressed.connect(self.pb_save_preset_pressed)

        layout1 = Qt.QHBoxLayout()
        layout1.addWidget(self.cb_preset_file, 1)
        layout1.addWidget(self.pb_add_file, 0)
        layout1.addWidget(self.pb_rem_file, 0)

        layout2 = Qt.QHBoxLayout()
        layout2.addWidget(self.cb_layer_presets, 1)
        layout2.addWidget(self.pb_save_preset, 0)
        layout2.addWidget(self.pb_add_preset, 0)
        layout2.addWidget(self.pb_rem_preset, 0)

        mainLayout = Qt.QVBoxLayout()
        mainLayout.addLayout(layout1)
        mainLayout.addLayout(layout2)
        mainLayout.addWidget(self.pb_activate)

        self.content_widget.setLayout(mainLayout)

        self.presets = {}
        self._app_index = 0
        self._user_index = 0

        self.update_presets()
        self.build_file_comboBox()
        self.build_preset_combobox()

        self.update_file_btn_state()

        self.cb_preset_file.currentIndexChanged.connect(self.preset_file_changed)

    def update_presets(self):
        self.presets = zlm_core.load_presets()

    def update_file_btn_state(self):
        enable = self.cb_preset_file.count() > 0 and self.cb_preset_file.currentIndex() >= self._user_index
        enable_2 = bool(self.cb_layer_presets.currentText())

        self.pb_rem_file.setEnabled(enable)
        self.pb_save_preset.setEnabled(enable and enable_2)
        self.pb_rem_preset.setEnabled(enable)
        self.pb_add_preset.setEnabled(enable)

        self.pb_activate.setEnabled(enable_2)

    def preset_file_changed(self, index):
        self.build_preset_combobox()
        self.update_file_btn_state()

    def build_file_comboBox(self):
        self.cb_preset_file.blockSignals(True)
        self.cb_preset_file.clear()
        # add the app first
        i = 0
        for main in ('app', 'user'):
            if main == 'app':
                self._app_index = i
            else:
                self._user_index = i

            for filename in self.presets[main]:
                self.cb_preset_file.addItem(filename)
                i += 1
        self.cb_preset_file.blockSignals(False)

    def build_preset_combobox(self):
        self.cb_layer_presets.clear()
        index = self.cb_preset_file.currentIndex()
        if index >= self._user_index:
            key = 'user'
        else:
            key = 'app'

        filename = self.cb_preset_file.currentText()

        try:
            self.cb_layer_presets.addItems(list(self.presets[key][filename].keys()))
        except:
            pass

    def get_current_preset_path(self):
        index = self.cb_preset_file.currentIndex()
        if index >= self._user_index:
            key = 'user'
        else:
            key = 'app'

        filename = self.cb_preset_file.currentText()
        presetname = self.cb_layer_presets.currentText()

        return key, filename, presetname

    def set_current_preset_path(self, path):
        self.cb_preset_file.blockSignals(True)
        try:
            key, filename, presetname = path

            main = self.presets[key]
            index = list(main.keys()).index(filename)
            if key == 'user':
                index += self._user_index
            self.cb_preset_file.setCurrentIndex(index)

            self.build_preset_combobox()

            preset = main[filename]
            index = list(preset.keys()).index(presetname)
            self.cb_layer_presets.setCurrentIndex(index)
        except:
            pass
        finally:
            self.cb_preset_file.blockSignals(False)
            self.update_file_btn_state()

    def get_current_preset(self):
        key, filename, presetname = self.get_current_preset_path()

        try:
            return self.presets[key][filename][presetname]
        except:
            pass
        return None

    def on_preset_activated(self):
        preset = self.get_current_preset()
        if preset:
            zlm_core.apply_preset(preset)
            self.preset_activated.emit()
            zlm_core.send_to_zbrush()

    def pb_add_file_pressed(self):
        dialog = Qt.QInputDialog(self)
        dialog.setInputMode(Qt.QInputDialog.InputMode.TextInput)
        dialog.setWindowTitle("Preset Name")
        dialog.setLabelText("Preset group name: ")
        dialog.setTextValue("new_preset_group")
        # lineEdit = dialog.findChild(Qt.QLineEdit)
        if dialog.exec():
            text = dialog.textValue()
            if zlm_core.validate_new_preset_file(text):
                zlm_core.create_new_preset_file(text)
                self.presets['user'][text] = {}
                self.build_file_comboBox()
                self.set_current_preset_path(('user', text, ''))
            else:
                Qt.QErrorMessage(self).showMessage('Invalid preset group name: "{}"'.format(text), "Invalid Preset Group Name")

    def pb_rem_file_pressed(self):
        key, group, _ = self.get_current_preset_path()
        test = Qt.QMessageBox.warning(self, "Remove Preset Group", 'This will remove preset group "{}".  Are you sure?'.format(group),
                                      Qt.QMessageBox.StandardButton.Yes, Qt.QMessageBox.StandardButton.No)
        if test == Qt.QMessageBox.StandardButton.Yes:
            index = self.cb_preset_file.currentIndex()

            zlm_core.remove_preset_file(group)

            self.presets[key].pop(group)
            self.build_file_comboBox()

            try:
                if index >= self.cb_preset_file.count():
                    index = self.cb_preset_file.count() - 1 
                self.cb_preset_file.setCurrentIndex(index)
            except:
                self.build_preset_combobox()

    def pb_add_preset_pressed(self):
        dialog = Qt.QInputDialog(self)
        dialog.setInputMode(Qt.QInputDialog.InputMode.TextInput)
        dialog.setWindowTitle("Preset Name")
        dialog.setLabelText("Preset name: ")
        dialog.setTextValue("preset_name")
        # lineEdit = dialog.findChild(Qt.QLineEdit)
        if dialog.exec():
            text = dialog.textValue()
            if text:
                key, group, _ = self.get_current_preset_path()
                if text in self.presets[key][group]:
                    test = Qt.QMessageBox.warning(self, "Preset already exists",
                                                  'Preset "{}" already exists and will be overridden. Do you want to continue?'.format(text),
                                                  Qt.QMessageBox.StandardButton.Yes, Qt.QMessageBox.StandardButton.No)

                    if test != Qt.QMessageBox.StandardButton.Yes:
                        return

                preset = zlm_core.get_layers_as_preset()
                self.presets[key][group][text] = preset
                zlm_core.save_layers_preset(group, self.presets[key][group])
                self.set_current_preset_path((key, group, text))

    def pb_rem_preset_pressed(self):
        key, group, preset = self.get_current_preset_path()
        test = Qt.QMessageBox.warning(self, "Remove Preset",
                            'Are you sure you want to delete preset "{}"?'.format(preset),
                            Qt.QMessageBox.StandardButton.Yes, Qt.QMessageBox.StandardButton.No)

        if test == Qt.QMessageBox.StandardButton.Yes:
            index = self.cb_layer_presets.currentIndex()

            self.presets[key][group].pop(preset)

            zlm_core.save_layers_preset(group, self.presets[key][group])

            self.build_preset_combobox()

            try:
                if index >= self.cb_layer_presets.count():
                    index = self.cb_layer_presets.count() - 1 
                self.cb_layer_presets.setCurrentIndex(index)
            except:
                pass

    def pb_save_preset_pressed(self):
        key, group, preset = self.get_current_preset_path()
        test = Qt.QMessageBox.warning(self, "Save Preset",
                            'Are you sure you want to override preset "{}"?'.format(preset),
                            Qt.QMessageBox.StandardButton.Yes, Qt.QMessageBox.StandardButton.No)

        if test == Qt.QMessageBox.StandardButton.Yes:
            self.presets[key][group][preset] = zlm_core.get_layers_as_preset()
            zlm_core.save_layers_preset(group, self.presets[key][group])
