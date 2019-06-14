import os

from PyQt5 import Qt, QtCore

from zlm_ui.settings_ui.base_setting_ui import SettingsTabBase, register_setting_tab


class CoreSettingWidget(SettingsTabBase):

    def __init__(self):
        SettingsTabBase.__init__(self, "Core")

        self.le_working_folder = Qt.QLineEdit()
        self.pb_working_browse = Qt.QPushButton(Qt.QIcon(":/folder.png"), "")
        self.pb_working_reset = Qt.QPushButton(Qt.QIcon(":/reset.png"), "")

        self.pb_working_browse.clicked.connect(self.browse_working_folder)
        self.pb_working_reset.clicked.connect(self.reset_working_folder)

        work_layout = Qt.QHBoxLayout()
        work_layout.addWidget(Qt.QLabel("File Folder: "), 0)
        work_layout.addWidget(self.le_working_folder, 1)
        work_layout.addWidget(self.pb_working_browse, 0)
        work_layout.addWidget(self.pb_working_reset, 0)

        layout = Qt.QVBoxLayout()
        layout.addLayout(work_layout)

        self.set_layout(layout)

    def browse_working_folder(self):
        directory = Qt.QFileDialog.getExistingDirectory(self, "Select file folder", self.le_working_folder.text())
        if directory:
            if os.name == 'nt':
                directory = directory.replace('/', '\\')
            self.le_working_folder.setText(directory)

    def reset_working_folder(self):
        self.le_working_folder.setText(self.DEFAULT_SETTINGS.working_folder)

    def reset_port(self):
        self.sb_com_port.setValue(self.DEFAULT_SETTINGS.communication_port)

    #
    # Base class method
    #

    def on_show(self):
        pass

    def on_close(self):
        pass

    def validate(self, settings):
        if not os.path.isdir(settings.working_folder):
            return False, "Invalid File Folder."
        return True, ""

    def save(self, settings):
        settings.working_folder = self.le_working_folder.text()

    def update(self, settings):
        self.le_working_folder.setText(settings.working_folder)


register_setting_tab(CoreSettingWidget)
