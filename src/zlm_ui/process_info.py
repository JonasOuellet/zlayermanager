from PyQt5 import QtWidgets, QtCore


class ProcesInfo(QtWidgets.QWidget):

    def __init__(self, parent, info) -> None:
        super().__init__(parent)

        self.setWindowTitle("Updating zbrush")

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint)
        # self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        lbl = QtWidgets.QLabel(info)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(lbl)

        self.setLayout(layout)
