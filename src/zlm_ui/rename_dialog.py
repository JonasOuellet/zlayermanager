from functools import partial

from PyQt5 import QtWidgets, QtCore, QtGui
from zlm_core import valid_name_re, max_name_len
from zlm_settings import ZlmSettings


class RenameDialog(QtWidgets.QDialog):
    def __init__(self, example='layerName', parent=None):
        super().__init__(
            parent,
            (QtCore.Qt.WindowType.WindowSystemMenuHint | QtCore.Qt.WindowType.WindowTitleHint |
             QtCore.Qt.WindowType.WindowCloseButtonHint)
        )

        self.setWindowTitle("Rename")

        self.base_name = example

        self.sb_remove_start = QtWidgets.QSpinBox()
        self.sb_remove_start.setMinimumWidth(50)
        self.sb_remove_start.setRange(0, 9)
        self.sb_remove_start.setObjectName('trim_start')

        self.sb_remove_end = QtWidgets.QSpinBox()
        self.sb_remove_end.setRange(0, 9)
        self.sb_remove_end.setMinimumWidth(50)
        self.sb_remove_end.setObjectName('trim_end')

        self.le_prefix = QtWidgets.QLineEdit()
        self.le_prefix.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(valid_name_re), self))
        self.le_prefix.setObjectName('prefix')

        self.le_suffix = QtWidgets.QLineEdit()
        self.le_suffix.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(valid_name_re), self))
        self.le_suffix.setObjectName('suffix')

        self.le_base_name = QtWidgets.QLineEdit()
        self.le_base_name.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(valid_name_re), self))
        # keep spaces for number
        self.le_base_name.setMaxLength(max_name_len - 2)
        self.le_base_name.setObjectName('basename')

        self.sb_padding = QtWidgets.QSpinBox()
        self.sb_padding.setRange(1, 4)
        self.sb_padding.setValue(2)
        self.sb_padding.setObjectName('padding')

        self.sb_start = QtWidgets.QSpinBox()
        self.sb_start.setRange(0, 999)
        self.sb_start.setObjectName('start')

        self.le_find = QtWidgets.QLineEdit()
        self.le_find.setObjectName('find')
        self.le_replace = QtWidgets.QLineEdit()
        self.le_replace.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(valid_name_re), self))
        self.le_replace.setObjectName('replace')

        self.lbl_ex = QtWidgets.QLabel('Example: ' + self.base_name + ' -> ')
        self.lbl_name = QtWidgets.QLabel(self.base_name)

        pb_accept = QtWidgets.QPushButton("Accept")
        pb_accept.clicked.connect(self.accept)
        pb_cancel = QtWidgets.QPushButton("Cancel")
        pb_cancel.clicked.connect(self.reject)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.sb_padding)
        layout.addWidget(QtWidgets.QLabel("start #: "))
        layout.addWidget(self.sb_start)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addStretch()
        layout2.addWidget(self.lbl_ex)
        layout2.addWidget(self.lbl_name)
        layout2.addStretch()

        grid = QtWidgets.QGridLayout()

        grid.addWidget(QtWidgets.QLabel("Find: "), 0, 0, 1, 1)
        grid.addWidget(self.le_find, 0, 1, 1, 2)
        grid.addWidget(QtWidgets.QLabel("Replace: "), 0, 3, 1, 1)
        grid.addWidget(self.le_replace, 0, 4, 1, 2)

        grid.addWidget(QtWidgets.QLabel("Strip start: "), 1, 0, 1, 1)
        grid.addWidget(self.sb_remove_start, 1, 1, 1, 1)
        grid.addItem(
            QtWidgets.QSpacerItem(
                0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
            ),
            1, 2, 1, 1
        )
        grid.addWidget(QtWidgets.QLabel("Strip end: "), 1, 3, 1, 1)
        grid.addWidget(self.sb_remove_end, 1, 4, 1, 1)
        grid.addItem(
            QtWidgets.QSpacerItem(
                0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
            ),
            1, 5, 1, 1
        )

        grid.addWidget(QtWidgets.QLabel("Base name: "), 2, 0, 1, 1)
        grid.addWidget(self.le_base_name, 2, 1, 1, 2)
        grid.addWidget(QtWidgets.QLabel('Padding: '), 2, 3, 1, 1)
        grid.addLayout(layout, 2, 4, 1, 2)

        grid.addWidget(QtWidgets.QLabel("Add prefix: "), 3, 0, 1, 1)
        grid.addWidget(self.le_prefix, 3, 1, 1, 2)
        grid.addWidget(QtWidgets.QLabel("Add suffix: "), 3, 3, 1, 1)
        grid.addWidget(self.le_suffix, 3, 4, 1, 2)

        grid.addLayout(layout2, 4, 0, 1, 6)

        grid.addItem(
            QtWidgets.QSpacerItem(
                0, 10, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
            ),
            5, 0, 1, 6
        )
        grid.addWidget(pb_accept, 6, 0, 1, 3)
        grid.addWidget(pb_cancel, 6, 3, 1, 3)

        self.setLayout(grid)

        self.setSizeGripEnabled(False)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)

        self.connect_widgets()

        self.settings = ZlmSettings.instance().get('rename_ui', {})
        self.load_settings()

    def showEvent(self, event):
        self.setFixedSize(self.sizeHint())

    def update_example(self):
        self.lbl_name.setText(self.rename([self.base_name])[0])

    def value_changed(self, widget, value):
        self.block_signals(True, (widget, ))
        # prefix, suffix and padding affect the len of base name
        if widget in (self.sb_padding, self.le_prefix, self.le_suffix, self.sb_start):
            self.update_base_name_len()

        self.update_example()
        self.block_signals(False, (widget, ))

    def update_base_name_len(self):
        pref = len(self.le_prefix.text())
        suf = len(self.le_suffix.text())
        pad = self.sb_padding.value()
        start = len(str(self.sb_start.value()))
        pad = max(pad, start)

        self.le_base_name.setMaxLength(max_name_len - pad - pref - suf)

    def rename(self, names: list[str]):
        find = self.le_find.text()
        replace = self.le_replace.text()

        strip_s = self.sb_remove_start.value()
        strip_e = 0 - self.sb_remove_end.value()

        base_name = self.le_base_name.text()
        padding = self.sb_padding.value()
        padding_str = '{{:0{}d}}'.format(padding)
        pad_start = self.sb_start.value()

        pref = self.le_prefix.text()
        suf = self.le_suffix.text()

        for x, name in enumerate(names):
            if find:
                name = name.replace(find, replace)

            name = name[strip_s:]
            if strip_e:
                name = name[:strip_e]

            if base_name:
                name = base_name + padding_str.format(pad_start + x)

            if pref:
                name = pref + name

            if suf:
                name += suf

            names[x] = name

        return names

    def connect_widgets(self):
        for child in self.children():
            cmd = partial(self.value_changed, child)
            if isinstance(child, QtWidgets.QSpinBox):
                child.valueChanged.connect(cmd)
            elif isinstance(child, QtWidgets.QLineEdit):
                child.textChanged.connect(cmd)

    def block_signals(self, block=True, excluded=()):
        for child in self.children():
            if child not in excluded:
                child.blockSignals(block)

    def load_settings(self):
        for child in self.children():
            obj_name = child.objectName()
            if obj_name in self.settings:
                if isinstance(child, QtWidgets.QSpinBox):
                    child.setValue(self.settings[obj_name])
                elif isinstance(child, QtWidgets.QLineEdit):
                    child.setText(self.settings[obj_name])

    def save_settings(self):
        for child in self.children():
            obj_name = child.objectName()
            if isinstance(child, QtWidgets.QSpinBox):
                self.settings[obj_name] = child.value()
            elif isinstance(child, QtWidgets.QLineEdit):
                self.settings[obj_name] = child.text()

    def accept(self):
        self.save_settings()
        QtWidgets.QDialog.accept(self)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    inst = RenameDialog()
    inst.show()
    exit_code = app.exec_()
    ZlmSettings.instance().save_to_file()
    sys.exit(exit_code)
