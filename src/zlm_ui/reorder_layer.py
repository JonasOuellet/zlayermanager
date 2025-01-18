from typing import List

from PyQt5 import QtWidgets, QtCore, QtGui

import zlm_core


class TableWidgetDragRows(QtWidgets.QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setColumnCount(1)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)

        self.build()

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)

    def build(self, layers: List[zlm_core.ZlmLayer] = None):
        if layers is None:
            layers = zlm_core.main_layers.instances_list
        self.setRowCount(len(layers))
        for x, layer in enumerate(layers):
            item = QtWidgets.QTableWidgetItem(layer.name)
            item.layer_inst = layer
            self.setItem(x, 0, item)

    def dropEvent(self, event: QtGui.QDropEvent):
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)

            rows = sorted(set(item.row() for item in self.selectedItems()))
            rows_to_move: List[zlm_core.ZlmLayer] = [self.item(row_index, 0).layer_inst for row_index in rows]

            for row_index in reversed(rows):
                self.removeRow(row_index)
                if row_index < drop_row:
                    drop_row -= 1

            for row_index, layer in enumerate(rows_to_move):
                row_index += drop_row
                self.insertRow(row_index)
                item = QtWidgets.QTableWidgetItem(layer.name)
                item.layer_inst = layer
                self.setItem(row_index, 0, item)

            event.accept()
            # for row_index in range(len(rows_to_move)):
            #     self.item(drop_row + row_index, 0).setSelected(True)
        super().dropEvent(event)

    def drop_on(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount()

        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def is_below(self, pos, index):
        rect = self.visualRect(index)
        margin = 2
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
        # noinspection PyTypeChecker
        return rect.contains(pos, True) and not (int(self.model().flags(index)) & QtCore.Qt.ItemFlag.ItemIsDropEnabled) and pos.y() >= rect.center().y()

    def get_layers(self) -> List[zlm_core.ZlmLayer]:
        return [self.item(x, 0).layer_inst for x in range(self.rowCount())]

    def alpha_sort(self, reverse=False):
        items = list(zlm_core.main_layers.instances_list)
        _sorted = sorted(items, key=lambda x: x.name, reverse=reverse)
        self.build(_sorted)

    def save_order(self, filepath):
        lines = [self.item(x, 0).text() for x in range(self.rowCount())]
        with open(filepath, mode='w') as f:
            f.write('\n'.join(lines))

    def load_order(self, filepath):
        try:
            with open(filepath, mode='r') as f:
                lines = f.readlines()
        except:
            QtWidgets.QMessageBox.critical(
                self,
                "Error foading file",
                "Error occured loading specified file."
            )
            return

        names = [line.strip() for line in lines]
        if len(names) != self.rowCount():
            QtWidgets.QMessageBox.critical(
                self,
                "Error foading file",
                "The file do not containt the same number of layers."
            )
            return

        layers = []
        for name in names:
            try:
                layer = zlm_core.main_layers.instances[name][0]
                layers.append(layer)
            except:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error foading file",
                    f"Coudln't find layer with name '{name}' in the current layer list."
                )
                return

        # update the table
        self.build(layers)


class ReorderLayerUI(QtWidgets.QDialog):

    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.setWindowTitle("Reorder Layers")

        self.table = TableWidgetDragRows()

        pb_accept = QtWidgets.QPushButton("Accept")
        pb_discard = QtWidgets.QPushButton("Discard")

        pb_accept.clicked.connect(self.accept)
        pb_discard.clicked.connect(self.reject)

        pb_save = QtWidgets.QPushButton(QtGui.QIcon(":/save.png"), "")
        pb_load = QtWidgets.QPushButton(QtGui.QIcon(":/folder.png"), "")

        pb_save.clicked.connect(self.save_order)
        pb_load.clicked.connect(self.load_order)

        pb_alpha_sort = QtWidgets.QPushButton(QtGui.QIcon(":/asort.png"), "")
        pb_alpha_sortinv = QtWidgets.QPushButton(QtGui.QIcon(":/asortinv.png"), "")
        pb_reset = QtWidgets.QPushButton(QtGui.QIcon(":/reset.png"), "")

        pb_alpha_sort.clicked.connect(lambda: self.table.alpha_sort())
        pb_alpha_sortinv.clicked.connect(lambda: self.table.alpha_sort(reverse=True))
        pb_reset.clicked.connect(lambda: self.table.build())

        if not self.is_names_valid():
            for btn in (pb_save, pb_load):
                btn.setToolTip(
                    "Multiple layer with the same name.  Make sure that each layer name is unique to use this feature."
                )
                btn.setDisabled(True)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(pb_save)
        top_layout.addWidget(pb_load)
        top_layout.addSpacing(20)
        top_layout.addWidget(pb_alpha_sort)
        top_layout.addWidget(pb_alpha_sortinv)
        top_layout.addStretch()
        top_layout.addWidget(pb_reset)

        layout = QtWidgets.QGridLayout()
        layout.addLayout(top_layout, 0, 0, 1, 2)
        layout.addWidget(self.table, 1, 0, 1, 2)

        layout.addWidget(pb_accept, 2, 0, 1, 1)
        layout.addWidget(pb_discard, 2, 1, 1, 1)

        self.setLayout(layout)

    def get_layers(self) -> List[zlm_core.ZlmLayer]:
        return self.table.get_layers()

    def is_names_valid(self) -> bool:
        """Validate that all layer have a unique name

        Returns:
            bool: _description_
        """
        for layer_name, instance in zlm_core.main_layers.instances.items():
            if len(instance) > 1:
                return False
        return True

    def save_order(self):
        _file, _filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Select order file to save",
            None,
            "txt (*.txt)"
        )
        if _file:
            self.table.save_order(_file)

    def load_order(self):
        _file, _filter = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select order file to load",
            None,
            "txt (*.txt)"
        )
        if _file:
            self.table.load_order(_file)
