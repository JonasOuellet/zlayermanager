from PySide2 import QtWidgets
import re


# solution found here:
# https://stackoverflow.com/questions/21030719/sort-a-pyside-qtgui-qtreewidget-by-an-alpha-numeric-column
# re-implement the QTreeWidgetItem
class ZlmTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, layer=None, parent=None):
        super(ZlmTreeWidgetItem, self).__init__(parent)
        self.layer = layer

        if self.layer:
            self.setText(0, layer.name)

    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        key1 = self.text(column)
        key2 = other.text(column)
        return self.natural_sort_key(key1) < self.natural_sort_key(key2)

    @staticmethod
    def natural_sort_key(key):
        regex = '(\d*\.\d+|\d+)'
        parts = re.split(regex, key)
        return tuple((e if i % 2 == 0 else float(e)) for i, e in enumerate(parts))


class ZlmLayerTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent):
        super(ZlmLayerTreeWidget, self).__init__(parent)
        self.mainUI = parent
        self.mainUI.closing.connect(self.onClose)
        self.mainUI.showing.connect(self.onShow)

        self.setSortingEnabled(True)
        column_names = ['Layer Name', 'Mode', 'Intensity']
        self.setColumnCount(len(column_names))
        self.setHeaderLabels(column_names)
        # self.setHeaderHidden(True)

        self.itemDict = {}

    def onClose(self):
        self.mainUI.settings['layerViewColumn'] = self.getColumnsWidth()

    def onShow(self):
        if 'layerViewColumn' in self.mainUI.settings:
            self.setColumnsWidth(self.mainUI.settings['layerViewColumn'])

    def getColumnsWidth(self):
        columnCount = self.columnCount()
        columnWidth = [60] * columnCount
        for x in range(columnCount):
            columnWidth[x] = self.columnWidth(x)

        return columnWidth

    def setColumnsWidth(self, width):
        # Set column With:
        for x, w in enumerate(width):
            if x < self.columnCount():
                self.setColumnWidth(x, w)

    def build(self):
        self.clear()
        self.itemDict = {}

        if self.mainUI.layers:
            for name, layerobj in self.mainUI.layers.items():
                item = ZlmTreeWidgetItem(layerobj)
                self.addTopLevelItem(item)
                self.itemDict[name] = item
