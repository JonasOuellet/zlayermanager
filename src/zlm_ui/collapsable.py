from PyQt5 import Qt


class ZlmCollapsableWidget(Qt.QWidget):
    def __init__(self, title=""):
        Qt.QWidget.__init__(self)

        self._pb_open = Qt.QPushButton(title)
        self._pb_open.setProperty('class', 'collapsable')
        self._pb_open.setCheckable(True)
        self._pb_open.setChecked(True)
        self._pb_open.toggled.connect(self.on_open_toggled)
        self.content_widget = Qt.QFrame()
        self.content_widget.setLineWidth(3)
        self.content_widget.setMidLineWidth(3)
        self.content_widget.setProperty('class', 'collapsable')

        layout = Qt.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._pb_open)
        layout.addWidget(self.content_widget)

        self.setLayout(layout)

    def on_open_toggled(self, state):
        if state:
            self.content_widget.show()
        else:
            self.content_widget.hide()

    def set_collapsed(self, collapse=True):
        if collapse:
            self._pb_open.setChecked(False)
            self.content_widget.hide()
        else:
            self._pb_open.setChecked(True)
            self.content_widget.show()

    def is_collapsed(self):
        return not self._pb_open.isChecked()

    def set_layout(self, layout):
        self.content_widget.setLayout(layout)
