from PySide2 import QtWidgets, QtCore
import zlm_core
from zlm_settings import ZlmSettings
from zlm_ui.zlm_layerTree import ZlmLayerTreeWidget


class ZlmMainUI(QtWidgets.QMainWindow):
    closing = QtCore.Signal()
    showing = QtCore.Signal()

    default_settings = {
        'geometry': None
    }

    def __init__(self, file_path=None):
        QtWidgets.QMainWindow.__init__(self)
        self.settings = ZlmSettings.instance().get('ui', self.default_settings)

        self.setWindowTitle("ZLayerManager")
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)

        self.tw_widget = ZlmLayerTreeWidget(self)
        self.lbl_subtool = QtWidgets.QLabel("SubTool: ")

        mainLayout = QtWidgets.QVBoxLayout()

        mainLayout.addWidget(self.lbl_subtool)
        mainLayout.addWidget(self.tw_widget)

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(mainLayout)
        self.setCentralWidget(self.central_widget)

        self.layers = None
        self.subTool = None

        if file_path:
            self.load_layers(file_path)

        geo = self.settings.get('geometry', None)
        if geo:
            self.setGeometry(*geo)

    def showEvent(self, event):
        self.showing.emit()

    def closeEvent(self, event):
        self.closing.emit()

        geo = self.geometry()
        self.settings['geometry'] = [geo.x(), geo.y(), geo.width(), geo.height()]

        ZlmSettings.instance().save_to_file()

    def load_layers(self, file_path):
        self.layers, self.subTool = zlm_core.parse_layer_file(file_path)
        self.tw_widget.build()
        self.update_subtool_label()

    def update_subtool_label(self):
        if self.subTool:
            self.lbl_subtool.setText("SubTool: " + self.subTool.name)
        else:
            self.lbl_subtool.setText("SubTool: ")
