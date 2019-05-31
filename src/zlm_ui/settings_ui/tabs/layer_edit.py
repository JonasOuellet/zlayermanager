import os

from PyQt5 import Qt, QtCore

from zlm_ui.settings_ui.base_setting_ui import SettingsTabBase, register_setting_tab
from zlm_ui import layer_edit_option as leo


move_down_warning = "Warning: Moving duplicated layer down the list may \
dramaticaly increase time to duplicate a layer.  By default, \
duplicated layer will be underneath the source layer."


class LayerEditSettingWidget(SettingsTabBase):

    def __init__(self):
        SettingsTabBase.__init__(self, "Layer Edit")

        self.pb_move_down = Qt.QPushButton("Move duplicated layer down")
        self.pb_move_down.setCheckable(True)

        self.pb_ask_bef_delete = Qt.QPushButton("Ask before delete")
        self.pb_ask_bef_delete.setCheckable(True)

        lbl = Qt.QLabel(move_down_warning)
        lbl.setWordWrap(True)

        layout = Qt.QGridLayout()
        layout.addWidget(lbl, 0, 0, 1, 2)
        layout.addWidget(self.pb_move_down, 1, 0, 1, 1)
        layout.addWidget(self.pb_ask_bef_delete, 1, 1, 1, 1)

        self.set_layout(layout)

    #
    # Base class method
    #

    def on_show(self):
        pass

    def on_close(self):
        pass

    def validate(self, settings):
        return True, ""

    def save(self, settings):
        options = settings.get(leo.option_name, leo.default_options)
        options[leo.ask_before_delete] = self.pb_ask_bef_delete.isChecked()
        options[leo.move_dup_layer_down] = self.pb_move_down.isChecked()

    def update(self, settings):
        options = settings.get(leo.option_name, leo.default_options)
        self.pb_ask_bef_delete.setChecked(options[leo.ask_before_delete])
        self.pb_move_down.setChecked(options[leo.move_dup_layer_down])


register_setting_tab(LayerEditSettingWidget)
