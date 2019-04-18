from PySide2 import QtWidgets, QtCore
from functools import partial


def is_valid_mode(mode, filter_mode):
    if filter_mode == 0:
        return True

    if filter_mode == 3 and mode == 1:
        return True

    if filter_mode == 1 and mode == 0:
        return True

    return filter_mode == mode


class LayerFilterWidget(QtWidgets.QWidget):
    filter_edited = QtCore.Signal(str, int)

    filter_option = ['All', 'Off', 'Active', 'Record']

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self)

        self.mainUI = parent
        self.mainUI.closing.connect(self.onClose)

        self.le_search_bar = QtWidgets.QLineEdit()
        self.le_search_bar.textEdited.connect(self._search_bar_changed)
        self.pb_filter = QtWidgets.QPushButton("Filter")

        self.current_filter = self.mainUI.settings.get('filter', 0)
        self.le_search_bar.setText(self.mainUI.settings.get('filterText', ''))

        self.filter_menu = self._build_menu()
        self.pb_filter.setMenu(self.filter_menu)

        layout = QtWidgets.QHBoxLayout()

        layout.addWidget(self.le_search_bar)
        layout.addWidget(self.pb_filter)

        self.setLayout(layout)

    def onClose(self):
        self.mainUI.settings['filterText'] = self.le_search_bar.text()
        self.mainUI.settings['filter'] = self.current_filter

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

    def setCurrentFilter(self, new_filter, toggled):
        if toggled:
            self.current_filter = self.filter_option.index(new_filter)
            self.filter_edited.emit(self.le_search_bar.text(), self.current_filter)

    def _search_bar_changed(self, text):
        self.filter_edited.emit(text, self.current_filter)
