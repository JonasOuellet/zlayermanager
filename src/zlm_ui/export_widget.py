from PyQt5 import Qt

from zlm_ui.collapsable import ZlmCollapsableWidget


class ZlmExportWidget(ZlmCollapsableWidget):

    def __init__(self):
        ZlmCollapsableWidget.__init__(self, 'Export:')

        self.pb_all = Qt.QPushButton('All')
        self.pb_sel = Qt.QPushButton('Selected')
        self.pb_active = Qt.QPushButton('Active')
        self.pb_record = Qt.QPushButton('Record')

        layout = Qt.QHBoxLayout()
        layout.addWidget(self.pb_all)
        layout.addWidget(self.pb_sel)
        layout.addWidget(self.pb_active)
        layout.addWidget(self.pb_record)

        self.content_widget.setLayout(layout)
