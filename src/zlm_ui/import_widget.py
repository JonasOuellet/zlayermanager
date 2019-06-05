from PyQt5 import Qt

from zlm_ui.collapsable import ZlmCollapsableWidget
from zlm_app import send_app_cmd


class ZlmImportWidget(ZlmCollapsableWidget):

    def __init__(self, main_ui):
        ZlmCollapsableWidget.__init__(self, 'Import:')

        self.main_ui = main_ui

        self.pb_sel = Qt.QPushButton('Selected as layer(s)')
        self.pb_sel.clicked.connect(self.export_layers)

        self.pb_base = Qt.QPushButton('Selected as base mesh')
        self.pb_base.clicked.connect(self.export_base)

        layout = Qt.QHBoxLayout()
        layout.addWidget(self.pb_sel)
        layout.addWidget(self.pb_base)

        self.set_layout(layout)

    def export_layers(self):
        command = "import zlm\nzlm.export_selected()"
        send_app_cmd(command)

    def export_base(self):
        command = "import zlm\nzlm.export_base()"
        send_app_cmd(command)
