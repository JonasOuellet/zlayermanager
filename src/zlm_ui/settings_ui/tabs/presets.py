import os

from PyQt5 import Qt, QtCore

from zlm_ui.settings_ui.base_setting_ui import SettingsTabBase, register_setting_tab


class PresetsEditSettingWidget(SettingsTabBase):

    def __init__(self):
        SettingsTabBase.__init__(self, "Presets")

        self.lw_directory = Qt.QListWidget()
        self.lw_directory.setMaximumHeight(100)

        self.pb_add = Qt.QPushButton(Qt.QIcon(":/add.png"), "")
        self.pb_remove = Qt.QPushButton(Qt.QIcon(":/remove.png"), "")
        self.pb_browse = Qt.QPushButton(Qt.QIcon(":/folder.png"), "")
        self.pb_reset = Qt.QPushButton(Qt.QIcon(":/reset.png"), "")

        self.pb_add.clicked.connect(self.add)
        self.pb_remove.clicked.connect(self.remove)
        self.pb_reset.clicked.connect(self.reset)
        self.pb_browse.clicked.connect(self.browse)

        bottom_layout = Qt.QHBoxLayout()
        bottom_layout.addWidget(self.pb_add)
        bottom_layout.addWidget(self.pb_remove)
        bottom_layout.addWidget(self.pb_browse)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.pb_reset)
        
        layout = Qt.QVBoxLayout()
        layout.addWidget(Qt.QLabel("Additionnal presets directory:"))
        layout.addWidget(self.lw_directory)
        layout.addLayout(bottom_layout)

        self.set_layout(layout)

    def _browse(self, starting_dir=None):
        directory = Qt.QFileDialog.getExistingDirectory(self, "Select presets folder", starting_dir)
        if directory:
            if os.name == 'nt':
                directory = directory.replace('/', '\\')
            return directory
        return None

    def add(self):
        directory = self._browse()
        if directory:
            self.lw_directory.addItem(directory)

    def remove(self):
        curRow  = self.lw_directory.currentRow()
        if curRow >= 0:
            self.lw_directory.takeItem(curRow)

    def reset(self):
        self.lw_directory.clear()

    def browse(self):
        for item in self.lw_directory.selectedItems():
            directory = self._browse(item.text())
            if directory:
                if os.name == 'nt':
                    directory = directory.replace('/', '\\')
                item.setText(directory)

    #
    # Base class method
    #

    def on_show(self):
        pass

    def on_close(self):
        pass

    def validate(self, settings):
        for directory in settings.additionnal_preset_dir:
            if not os.path.isdir(directory):
                return False, f'Invalid presets path: "{directory}"'
        return True, ""

    def save(self, settings):
        settings.additionnal_preset_dir = [self.lw_directory.item(x).text() for x in range(self.lw_directory.count())]

    def update(self, settings):
        self.lw_directory.clear()
        self.lw_directory.addItems(settings.additionnal_preset_dir)


register_setting_tab(PresetsEditSettingWidget)
