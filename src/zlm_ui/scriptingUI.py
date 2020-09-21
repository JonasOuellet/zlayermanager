import sys
import contextlib
import traceback

from PyQt5 import Qt, QtCore

from zlm_settings import ZlmSettings



class ScriptWidget(Qt.QPlainTextEdit):
    executeSelectedRequested = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWordWrapMode(Qt.QTextOption.NoWrap)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter:
            cursor = self.textCursor()
            to_exec = self.toPlainText()[cursor.selectionStart(): cursor.selectionEnd()]
            if to_exec:
                self.executeSelectedRequested.emit(to_exec)
                return
        if event.key() == QtCore.Qt.Key_Tab:
            # insert four spaces at cursor position
            # TODO: handle selection
            self.insertPlainText('    ')
            return
        return super().keyPressEvent(event)


class OutputWidget(Qt.QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWordWrapMode(Qt.QTextOption.NoWrap)
        self.setTextColor(Qt.Qt.white)

    def write(self, text):
        self.append(text)
        # need to call this to update text during python execution
        Qt.qApp.processEvents()

    def error(self, text):
        self.setTextColor(Qt.Qt.red)
        self.append(text)
        self.setTextColor(Qt.Qt.white)
        # need to call this to update text during python execution
        Qt.qApp.processEvents()


class ZlmScriptingUI(Qt.QMainWindow):
    # closing = QtCore.pyqtSignal()
    # showing = QtCore.pyqtSignal()

    # settings_changed = QtCore.pyqtSignal()

    _instance = None
    _pythonFrame = {} 

    default_settings = {
        'geometry': None
    }

    def __init__(self, parent=None):
        Qt.QMainWindow.__init__(self, parent)

        self.settings = ZlmSettings.instance().get('scripting', self.default_settings)
        self.setWindowTitle("Script Editor")

        self.layout = Qt.QVBoxLayout()

        self.outputWindow = OutputWidget()
        self.outputWindow.setReadOnly(True)

        self.scriptsWidget = []
        # self.scriptsWidget.append()

        tab1 = ScriptWidget()
        tab1.executeSelectedRequested.connect(self._execSelected)
        self.scriptsWidget.append(tab1)

        self.scriptTab = Qt.QTabWidget()
        self.scriptTab.addTab(tab1, "Tab1")

        self.layout.addWidget(self.outputWindow)
        self.layout.addWidget(self.scriptTab)

        centralWidget = Qt.QWidget()
        centralWidget.setLayout(self.layout)
        self.setCentralWidget(centralWidget)

        geo = self.settings.get('geometry', None)
        if geo:
            self.setGeometry(*geo)

    @staticmethod
    def theOne(parent=None):
        if not ZlmScriptingUI._instance:
            ZlmScriptingUI._instance = ZlmScriptingUI(parent)
        return ZlmScriptingUI._instance

    def moveEvent(self, event):
        geo = self.geometry()
        self.settings['geometry'] = [geo.x(), geo.y(), geo.width(), geo.height()]

    def resizeEvent(self, event):
        geo = self.geometry()
        self.settings['geometry'] = [geo.x(), geo.y(), geo.width(), geo.height()]

    def _execSelected(self, text):
        lines = text.splitlines()
        for line in lines:
            self.outputWindow.write(f">>> {line}\n")

        try:
            with self._redirectOutput() as s:
                exec(text, ZlmScriptingUI._pythonFrame)
        except Exception as e:
            err = traceback.format_exc()
            self.outputWindow.error(err)

    @contextlib.contextmanager
    def _redirectOutput(self):
        old = sys.stdout
        stdout = self.outputWindow
        sys.stdout = stdout
        yield stdout
        sys.stdout = old
