import re

from PyQt5 import QtWidgets, QtCore, QtGui

import zlm_core
from zlm_ui.collapsable import ZlmCollapsableWidget
import zlm_to_zbrush


class ZlmPresetWidget(ZlmCollapsableWidget):
    preset_activated = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__("Presets: ")

        self.cb_preset_file = QtWidgets.QComboBox()
        self.cb_layer_presets = QtWidgets.QComboBox()
        self.pb_activate = QtWidgets.QPushButton('Activate')
        self.pb_activate.clicked.connect(self.on_preset_activated)

        self.pb_add_file = QtWidgets.QPushButton(QtGui.QIcon(':/add.png'), '')
        self.pb_add_file.clicked.connect(self.pb_add_file_clicked)
        self.pb_rem_file = QtWidgets.QPushButton(QtGui.QIcon(':/remove.png'), '')
        self.pb_rem_file.clicked.connect(self.pb_rem_file_clicked)

        self.pb_add_preset = QtWidgets.QPushButton(QtGui.QIcon(':/add.png'), '')
        self.pb_add_preset.clicked.connect(self.pb_add_preset_clicked)
        self.pb_rem_preset = QtWidgets.QPushButton(QtGui.QIcon(':/remove.png'), '')
        self.pb_rem_preset.clicked.connect(self.pb_rem_preset_clicked)
        self.pb_save_preset = QtWidgets.QPushButton(QtGui.QIcon(':/save.png'), '')
        self.pb_save_preset.clicked.connect(self.pb_save_preset_clicked)

        layout1 = QtWidgets.QHBoxLayout()
        layout1.addWidget(self.cb_preset_file, 1)
        layout1.addWidget(self.pb_add_file, 0)
        layout1.addWidget(self.pb_rem_file, 0)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(self.cb_layer_presets, 1)
        layout2.addWidget(self.pb_save_preset, 0)
        layout2.addWidget(self.pb_add_preset, 0)
        layout2.addWidget(self.pb_rem_preset, 0)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(layout1)
        mainLayout.addLayout(layout2)
        mainLayout.addWidget(self.pb_activate)

        self.set_layout(mainLayout)

        self.presets = {}
        self._app_index = 0
        self._user_index = 0

        self.build_presets()

        self.cb_preset_file.currentIndexChanged.connect(self.preset_file_changed)

    def build_presets(self):
        self.update_presets()
        self.build_file_comboBox()
        self.build_preset_combobox()

    def update_presets(self):
        self.presets = zlm_core.load_presets()

    def update_file_btn_state(self):
        enable = self.cb_preset_file.count() > 0 and self.cb_preset_file.currentIndex() >= self._user_index
        enable_2 = bool(self.cb_layer_presets.currentText())

        self.pb_rem_file.setEnabled(enable)
        self.pb_save_preset.setEnabled(enable and enable_2)
        self.pb_rem_preset.setEnabled(enable and enable_2)
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

        self.update_file_btn_state()

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
        self.update_file_btn_state()

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
        if preset is not None:
            # to avoid any error in preset file.
            try:
                zlm_core.apply_preset(preset)
            except:
                pass
            self.preset_activated.emit()
            zlm_to_zbrush.send_to_zbrush()

    def pb_add_file_clicked(self):
        text = self.ask_for_name("Preset Name", "Preset group name: ", "new_preset_group")
        if text:
            name = self.validate_name(text, set(list(self.presets['app'].keys()) + list(self.presets['user'].keys())))
            zlm_core.create_new_preset_file(name)
            self.presets['user'][name] = {}
            self.build_file_comboBox()
            self.set_current_preset_path(('user', name, ''))

    def validate_name(self, name, _set):
        if name not in _set:
            return name

        number = 1
        # replace number with new number
        match = re.search(r'(\d+)$', name)
        if match:
            name = name[:match.span()[0]]
            number = int(match.group(0)) + 1

        name = f'{name}{number:02d}'
        return self.validate_name(name, _set)

    def pb_rem_file_clicked(self):
        key, group, _ = self.get_current_preset_path()
        test = QtWidgets.QMessageBox.warning(
            self,
            "Remove Preset Group",
            f'This will remove preset group "{group}".  Are you sure?',
            QtWidgets.QMessageBox.StandardButton.Yes,
            QtWidgets.QMessageBox.StandardButton.No
        )
        if test == QtWidgets.QMessageBox.StandardButton.Yes:
            index = self.cb_preset_file.currentIndex()

            zlm_core.remove_preset_file(group)

            self.presets[key].pop(group)
            self.build_file_comboBox()

            if index >= self.cb_preset_file.count():
                index = self.cb_preset_file.count() - 1

            if index < 0:
                self.build_preset_combobox()
            else:
                self.cb_preset_file.setCurrentIndex(index)

    def pb_add_preset_clicked(self):
        text = self.ask_for_name("Preset Name", "Preset name: ", "preset_name")
        if text:
            key, group, _ = self.get_current_preset_path()

            name = self.validate_name(text, self.presets[key][group].keys())

            preset = zlm_core.get_layers_as_preset()
            self.presets[key][group][name] = preset
            zlm_core.save_layers_preset(group, self.presets[key][group])
            self.set_current_preset_path((key, group, name))

    def pb_rem_preset_clicked(self):
        key, group, preset = self.get_current_preset_path()
        test = QtWidgets.QMessageBox.warning(
            self,
            "Remove Preset",
            f'Are you sure you want to delete preset "{preset}"?',
            QtWidgets.QMessageBox.StandardButton.Yes,
            QtWidgets.QMessageBox.StandardButton.No
        )

        if test == QtWidgets.QMessageBox.StandardButton.Yes:
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

    def pb_save_preset_clicked(self):
        key, group, preset = self.get_current_preset_path()
        test = QtWidgets.QMessageBox.warning(
            self,
            "Save Preset",
            f'Are you sure you want to override preset "{preset}"?',
            QtWidgets.QMessageBox.StandardButton.Yes,
            QtWidgets.QMessageBox.StandardButton.No
        )

        if test == QtWidgets.QMessageBox.StandardButton.Yes:
            self.presets[key][group][preset] = zlm_core.get_layers_as_preset()

            try:
                zlm_core.save_layers_preset(group, self.presets[key][group])
            except:
                # catch exception if cannot write to file.
                pass

    def ask_for_name(self, title='Enter Name', label='Name: ', text=''):
        dialog = QtWidgets.QInputDialog(self)
        dialog.setInputMode(QtWidgets.QInputDialog.InputMode.TextInput)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setTextValue(text)
        # https://forum.qt.io/topic/9171/solved-how-can-a-lineedit-accept-only-ascii-alphanumeric-character-required-a-z-a-z-0-9/4
        lineEdit: QtWidgets.QLineEdit = dialog.findChild(QtWidgets.QLineEdit)
        lineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[A-Za-z0-9_]+"), dialog))
        if dialog.exec():
            return dialog.textValue()
        return None
