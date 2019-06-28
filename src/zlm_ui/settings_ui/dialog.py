import copy

from PyQt5 import Qt, QtCore

import zlm_settings
from zlm_ui.settings_ui import base_setting_ui as base_ui


class SettingsDialog(Qt.QDialog):
    def __init__(self, main_ui):
        Qt.QDialog.__init__(self, main_ui, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle("Zlm Settings")

        self.settings_tabs = base_ui.get_tab_instances()
        # build default settings
        default_settings = {
                'tabs': {},
                'geometry': None
            }
        for tab in self.settings_tabs:
            d = default_settings['tabs'][tab.name] = {
                'collapsed': False
            }

        settings = zlm_settings.ZlmSettings.instance()
        self.settings = settings.get("settings_ui", default_settings)

        widget_layout = Qt.QVBoxLayout()

        # set collapsed and update ui
        for tab in self.settings_tabs:
            tab.set_collapsed(self.settings['tabs'][tab.name]['collapsed'])
            tab.update(settings)
            widget_layout.addWidget(tab)

        widget_layout.addStretch()

        pb_accept = Qt.QPushButton("Accept")
        pb_discard = Qt.QPushButton("Discard")

        pb_accept.clicked.connect(self.accept_settings)
        pb_discard.clicked.connect(self.discard_settings)

        main_widget = Qt.QWidget()

        main_widget.setLayout(widget_layout)

        scroll_area = Qt.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_widget)

        bottom_layout = Qt.QHBoxLayout()
        bottom_layout.setContentsMargins(10, 5, 10, 10)
        bottom_layout.addWidget(pb_accept)
        bottom_layout.addWidget(pb_discard)

        main_layout = Qt.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        if self.settings['geometry'] is not None:
            try:
                self.setGeometry(*self.settings['geometry'])
            except:
                pass

    def save_state(self):
        for tab in self.settings_tabs:
            tab.on_close()
            self.settings['tabs'][tab.name]['collapsed'] = tab.is_collapsed()

        geo = self.geometry()
        self.settings['geometry'] = [geo.x(), geo.y(), geo.width(), geo.height()]

    def accept_settings(self):
        self.save_state()

        settings = zlm_settings.ZlmSettings.instance()
        settings_tmp = copy.deepcopy(settings)
        for tab in self.settings_tabs:
            try:
                tab.save(settings_tmp)
            except Exception as e:
                Qt.QMessageBox.critical(self, "Settings Value Error", str(e))
                return

        for tab in self.settings_tabs:
            valid, error = tab.validate(settings_tmp)
            if not valid:
                Qt.QMessageBox.critical(self, "Settings Value Error", error)
                return

        # save to real settings
        for tab in self.settings_tabs:
            tab.save(settings)

        settings.save_to_file()
        self.accept()

    def discard_settings(self):
        self.reject()

    def showEvent(self, event):
        for tab in self.settings_tabs:
            tab.on_show()

    def reject(self):
        self.save_state()
        Qt.QDialog.reject(self)
