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

        self.pb_always_on_top = Qt.QPushButton("Window always on top")
        self.pb_always_on_top.setCheckable(True)

        self.pb_check_for_updates = Qt.QPushButton("Check for updates")
        self.pb_check_for_updates.setCheckable(True)

        work_layout = Qt.QHBoxLayout()
        work_layout.addWidget(Qt.QLabel("File Folder: "), 0)
        work_layout.addWidget(self.le_working_folder, 1)
        work_layout.addWidget(self.pb_working_browse, 0)
        work_layout.addWidget(self.pb_working_reset, 0)

        bottom_layout = Qt.QHBoxLayout()
        bottom_layout.addWidget(self.pb_always_on_top)
        bottom_layout.addWidget(self.pb_check_for_updates)
        bottom_layout.addStretch()

        layout = Qt.QVBoxLayout()
        layout.addLayout(work_layout)
        layout.addLayout(bottom_layout)

        self.set_layout(layout)

    def browse_working_folder(self):
        directory = Qt.QFileDialog.getExistingDirectory(self, "Select file folder", self.le_working_folder.text())
        if directory:
            if os.name == 'nt':
                directory = directory.replace('/', '\\')
            self.le_working_folder.setText(directory)

    def reset_working_folder(self):
        self.le_working_folder.setText(self.DEFAULT_SETTINGS.working_folder)

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
        try:
            settings['ui']['always_on_top'] = self.pb_always_on_top.isChecked()
        except:
            pass

        settings.check_for_updates = self.pb_check_for_updates.isChecked()

    def update(self, settings):
        self.le_working_folder.setText(settings.working_folder)
        try:
            self.pb_always_on_top.setChecked(settings['ui']['always_on_top'])
        except:
            self.pb_always_on_top.setChecked(False)

        self.pb_check_for_updates.setChecked(settings.check_for_updates)

register_setting_tab(CoreSettingWidget)
