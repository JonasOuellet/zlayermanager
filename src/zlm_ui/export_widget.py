from PySide2 import QtWidgets

from zlm_ui.collapsable import ZlmCollapsableWidget


class ZlmExportWidget(ZlmCollapsableWidget):

    def __init__(self):
        ZlmCollapsableWidget.__init__(self, 'Export:')

        self.pb_all = QtWidgets.QPushButton('All')
        self.pb_sel = QtWidgets.QPushButton('Selected')
        self.pb_active = QtWidgets.QPushButton('Active')
        self.pb_record = QtWidgets.QPushButton('Record')

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.pb_all)
        layout.addWidget(self.pb_sel)
        layout.addWidget(self.pb_active)
        layout.addWidget(self.pb_record)

        self.content_widget.setLayout(layout)
