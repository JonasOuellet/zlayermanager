from PyQt5 import Qt, QtCore

import zlm_settings
from zlm_ui.collapsable import ZlmCollapsableWidget


_SETTINGS_TABS = []


class SettingsTabBase(ZlmCollapsableWidget):

    DEFAULT_SETTINGS = zlm_settings.ZlmSettings(False)

    def __init__(self, name):
        ZlmCollapsableWidget.__init__(self, name)
        self.name = name

    def set_layout(self, layout):
        self.content_widget.setLayout(layout)

    def validate(self, settings):
        """ check if settings are valid

        Args:
            settings (type): Settings to validate

        Returns:
            (bool, str): return if the message is valid and the error message.
        """

        return True, ""

    def save(self, settings):
        """Save current ui settings state in the settings dict.

        Args:
            settings (dict): settings to save to
        """
        pass

    def update(self, settings):
        """Update UI state with current settings

        Args:
            settings (dict): Settings to update UI with
        """
        pass

    def on_close(self):
        pass

    def on_show(self):
        pass


def register_setting_tab(cls):
    _SETTINGS_TABS.append(cls)


def get_tab_instances():
    return [cls() for cls in _SETTINGS_TABS]
