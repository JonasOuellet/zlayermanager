from PySide2 import QtWidgets, QtCore

import zlm_core


class ZlmPresetWidget(QtWidgets.QWidget):
    preset_activated = QtCore.Signal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.cb_preset_file = QtWidgets.QComboBox()
        self.cb_layer_presets = QtWidgets.QComboBox()
        pb_activate = QtWidgets.QPushButton('Activate')
        pb_activate.clicked.connect(self.on_preset_activated)

        layout1 = QtWidgets.QHBoxLayout()
        layout1.addWidget(self.cb_preset_file)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(self.cb_layer_presets)
        layout2.addWidget(pb_activate)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(layout1)
        mainLayout.addLayout(layout2)

        self.setLayout(mainLayout)

        self.presets = {}
        self._app_index = 0
        self._user_index = 0

        self.presets = zlm_core.load_presets()
        self.build_file_comboBox()
        self.build_preset_combobox()

    def build_file_comboBox(self):
        self.cb_preset_file.clear()
        # add the app first
        i = 0
        for main in ('app', 'user'):
            if main == 'app':
                self._app_index = i
                # self.cb_preset_file.addItem("App--------------")
            else:
                self._user_index = i
                # self.cb_preset_file.addItem("User-------------")

            for filename in self.presets[main]:
                self.cb_preset_file.addItem(filename)
                i += 1

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
        except Exception as e:
            print(e)

    def get_current_preset(self):
        index = self.cb_preset_file.currentIndex()
        if index >= self._user_index:
            key = 'user'
        else:
            key = 'app'

        filename = self.cb_preset_file.currentText()
        presetname = self.cb_layer_presets.currentText()

        try:
            return self.presets[key][filename][presetname]
        except Exception as e:
            print(e)
        return None

    def on_preset_activated(self):
        preset = self.get_current_preset()
        if preset:
            zlm_core.apply_preset(preset)
            self.preset_activated.emit()
            zlm_core.send_to_zbrush()
