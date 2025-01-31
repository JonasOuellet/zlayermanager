from typing import TYPE_CHECKING
from functools import partial

from PyQt5 import QtWidgets, QtCore, QtGui

if TYPE_CHECKING:
    from zlm_ui.main_ui import ZlmMainUI


def is_valid_mode(mode, filter_mode):
    if filter_mode == 0:
        return True

    if filter_mode == 2 and mode >= 1:
        return True

    if filter_mode == 4 and mode == 1:
        return True

    if filter_mode == 1 and mode == 0:
        return True

    if filter_mode == 3 and mode == 2:
        return True

    return False


class LayerFilterWidget(QtWidgets.QWidget):
    filter_edited = QtCore.pyqtSignal(str, int)

    filter_option = ['All', 'Off', 'Active/Record', 'Active', 'Record']

    def __init__(self, parent: "ZlmMainUI"):
        super().__init__(parent)

        self.main_ui = parent
        self.main_ui.closing.connect(self.on_close)

        self.le_search_bar = QtWidgets.QLineEdit()
        self.le_search_bar.textEdited.connect(self._search_bar_changed)
        self.pb_filter = QtWidgets.QPushButton(QtGui.QIcon(":/filter.png"), " ")

        self.current_filter = self.main_ui.settings.get('filter', 0)
        self.le_search_bar.setText(self.main_ui.settings.get('filterText', ''))

        self.filter_menu = self._build_menu()
        self.pb_filter.setMenu(self.filter_menu)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.le_search_bar)
        layout.addWidget(self.pb_filter)

        self.setLayout(layout)

    def on_close(self):
        self.main_ui.settings['filterText'] = self.le_search_bar.text()
        self.main_ui.settings['filter'] = self.current_filter

    def _build_menu(self):
        menu = QtWidgets.QMenu(self)

        group = QtWidgets.QActionGroup(menu)

        for x, filt in enumerate(self.filter_option):
            action1 = QtWidgets.QAction(filt, menu)
            action1.setCheckable(True)
            group.addAction(action1)
            menu.addAction(action1)

            if x == self.current_filter:
                action1.setChecked(True)

            action1.toggled.connect(partial(self.setCurrentFilter, filt))

        return menu

    def setCurrentFilter(self, new_filter: str, toggled: bool):
        if toggled:
            self.current_filter = self.filter_option.index(new_filter)
            self.filter_edited.emit(self.le_search_bar.text().lower(),
                                    self.current_filter)

    def _search_bar_changed(self, text: str):
        self.filter_edited.emit(text.lower(), self.current_filter)
