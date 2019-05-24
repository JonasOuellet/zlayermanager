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

        self.sb_com_port = Qt.QSpinBox()
        self.sb_com_port.setRange(1000, 9999)

        self.pb_reset_port = Qt.QPushButton(Qt.QIcon(":/reset.png"), "")

        self.pb_reset_port.clicked.connect(self.reset_port)

        work_layout = Qt.QHBoxLayout()
        work_layout.addWidget(Qt.QLabel("File Folder: "), 0)
        work_layout.addWidget(self.le_working_folder, 1)
        work_layout.addWidget(self.pb_working_browse, 0)
        work_layout.addWidget(self.pb_working_reset, 0)

        port_layout = Qt.QHBoxLayout()
        port_layout.addStretch()
        port_layout.addWidget(Qt.QLabel("Port: "), 0)
        port_layout.addWidget(self.sb_com_port, 0)
        port_layout.addWidget(self.pb_reset_port, 0)

        layout = Qt.QVBoxLayout()
        layout.addLayout(work_layout)
        layout.addLayout(port_layout)

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
        settings.communication_port = self.sb_com_port.value()

    def update(self, settings):
        self.sb_com_port.setValue(settings.communication_port)
        self.le_working_folder.setText(settings.working_folder)


register_setting_tab(CoreSettingWidget)
