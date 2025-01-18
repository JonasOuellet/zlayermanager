from typing import TYPE_CHECKING

from PyQt5 import QtWidgets, QtCore

from zlm_ui.collapsable import ZlmCollapsableWidget


if TYPE_CHECKING:
    from zlm_ui.main_ui import ZlmMainUI


class ZlmExportWidget(ZlmCollapsableWidget):

    def __init__(self, main_ui: "ZlmMainUI"):
        super().__init__('Export:')

        self.main_ui = main_ui

        self.pb_all = QtWidgets.QPushButton('All')
        self.pb_sel = QtWidgets.QPushButton('Selected')
        self.pb_active = QtWidgets.QPushButton('Active')
        self.pb_record = QtWidgets.QPushButton('Record')

        self.pb_base = QtWidgets.QPushButton("Base Mesh")

        self.sb_subdiv = QtWidgets.QSpinBox()
        self.sb_subdiv.setRange(1, 99)
        self.sb_subdiv.setMinimumWidth(40)
        self.sb_subdiv.setValue(self.main_ui.settings.get('subdiv', 1))

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(QtWidgets.QLabel("Subdivision: "))
        layout2.addWidget(self.sb_subdiv)

        main_layout = QtWidgets.QGridLayout()
        main_layout.addWidget(self.pb_all, 0, 0, 1, 1)
        main_layout.addWidget(self.pb_sel, 0, 1, 1, 1)
        main_layout.addWidget(self.pb_active, 0, 2, 1, 1)
        main_layout.addWidget(self.pb_record, 0, 3, 1, 1)

        # row 1
        main_layout.addWidget(self.pb_base, 1, 0, 1, 1)
        main_layout.addLayout(layout2, 1, 1, 1, 3, QtCore.Qt.AlignmentFlag.AlignRight)

        self.set_layout(main_layout)

    def get_subdiv(self):
        return self.sb_subdiv.value()

    def on_close(self):
        self.main_ui.settings['subdiv'] = self.get_subdiv()
