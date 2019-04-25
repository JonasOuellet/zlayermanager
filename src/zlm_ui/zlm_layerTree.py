from PySide2 import QtWidgets, QtCore
import re
from zlm_core import ZlmLayerMode, ZlmLayer, send_to_zbrush, send_intensity
from zlm_ui.filter_widget import is_valid_mode


# Use delegate to make it faster ?
# https://stackoverflow.com/questions/7175333/how-to-create-delegate-for-qtreewidget

class NoWheelSlider(QtWidgets.QSlider):
    def __init__(self):
        QtWidgets.QSlider.__init__(self, QtCore.Qt.Horizontal)
        self.setRange(0, 100)

    def wheelEvent(self, event):
        pass


class ZlmIntensity(QtWidgets.QWidget):
    slider_pressed = QtCore.Signal(object, float)
    slider_released = QtCore.Signal(object, float)
    slider_moved = QtCore.Signal(object, float)

    spin_box_changed = QtCore.Signal(object, float)
    
    def __init__(self, item, intensity=1.0):
        QtWidgets.QWidget.__init__(self)
        self.item = item

        self.slider = NoWheelSlider()
        
        self.spinBox = QtWidgets.QDoubleSpinBox()
        self.spinBox.setSingleStep(0.1)
        self.spinBox.setRange(0, 1.0)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.spinBox)

        self.setLayout(layout)

        self.slider.sliderMoved.connect(self._sliderMoved)
        self.slider.sliderPressed.connect(self._slider_pressed)
        self.slider.sliderReleased.connect(self._slider_released)
        self.spinBox.valueChanged.connect(self._spinBoxChanged)

    def set_intensity(self, value):
        self.spinBox.blockSignals(True)
        self.slider.setValue(value * 100)
        self.spinBox.setValue(value)
        self.spinBox.blockSignals(False)

    def _sliderMoved(self, value):
        f_value = value/100.0
        self.spinBox.blockSignals(True)
        self.spinBox.setValue(f_value)
        self.spinBox.blockSignals(False)

        self.slider_moved.emit(self.item, f_value)

    def _spinBoxChanged(self, value):
        self.slider.setValue(int(value*100))
        self.spin_box_changed.emit(self.item, value)

    def _slider_pressed(self):
        self.slider_pressed.emit(self.item, self.spinBox.value())

    def _slider_released(self):
        self.slider_released.emit(self.item, self.spinBox.value())


class ZlmModeWidget(QtWidgets.QWidget):
    mode_changed = QtCore.Signal(object, object)

    def __init__(self, item, mode=ZlmLayerMode.off):
        QtWidgets.QWidget.__init__(self)

        self.item = item

        layout = QtWidgets.QHBoxLayout()
        self.pb_on = QtWidgets.QPushButton("On")
        self.pb_on.setCheckable(True)
        self.pb_on.setMaximumSize(QtCore.QSize(32, 32))
        self.pb_rect = QtWidgets.QPushButton("R")
        self.pb_rect.setCheckable(True)
        self.pb_rect.setMaximumSize(QtCore.QSize(32, 32))

        layout.addWidget(self.pb_on)
        layout.addWidget(self.pb_rect)

        self.setLayout(layout)

        self.setMode(mode)

        self.pb_on.toggled.connect(self.pb_on_toggled)
        self.pb_rect.toggled.connect(self.pb_rect_toggled)

    def setMode(self, mode, emit=False):
        if not emit:
            self.pb_on.blockSignals(True)
            self.pb_rect.blockSignals(True)

        if mode == ZlmLayerMode.off:
            self.pb_on.setChecked(False)
            self.pb_rect.setChecked(False)
        elif mode == ZlmLayerMode.active:
            self.pb_on.setChecked(True)
            self.pb_rect.setChecked(False)
        elif mode == ZlmLayerMode.record:
            self.pb_on.setChecked(True)
            self.pb_rect.setChecked(True)

        if not emit:
            self.pb_on.blockSignals(False)
            self.pb_rect.blockSignals(False)

    def getMode(self):
        if self.pb_on.isChecked():
            if self.pb_rect.isChecked():
                return ZlmLayerMode.record
            return ZlmLayerMode.active
        return ZlmLayerMode.off

    def pb_on_toggled(self, state):
        if not state:
            self.pb_rect.blockSignals(True)
            self.pb_rect.setChecked(False)
            self.pb_rect.blockSignals(False)
        mode = self.getMode()
        self.mode_changed.emit(self.item, mode)

    def pb_rect_toggled(self, state):
        if state:
            self.pb_on.blockSignals(True)
            self.pb_on.setChecked(True)
            self.pb_on.blockSignals(False)
        mode = self.getMode()
        self.mode_changed.emit(self.item, mode)


# solution found here:
# https://stackoverflow.com/questions/21030719/sort-a-pyside-qtgui-qtreewidget-by-an-alpha-numeric-column
# re-implement the QTreeWidgetItem
class ZlmTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, layer=None):
        super(ZlmTreeWidgetItem, self).__init__(parent)
        self.tree_widget = parent
        self.layer = layer

        self.mode_widget = ZlmModeWidget(self)
        self.intensity_widget = ZlmIntensity(self)

        if self.layer:
            self.setText(0, str(layer.index))
            self.setText(1, layer.name)
            self.mode_widget.setMode(self.layer.mode)
            self.intensity_widget.set_intensity(self.layer.intensity)

        self.tree_widget.setItemWidget(self, 2, self.mode_widget)
        self.tree_widget.setItemWidget(self, 3, self.intensity_widget)

        self.mode_widget.mode_changed.connect(self.tree_widget.on_item_mode_changed)
        self.intensity_widget.slider_pressed.connect(self.tree_widget.on_item_slider_pressed)
        self.intensity_widget.slider_moved.connect(self.tree_widget.on_item_slider_moved)
        self.intensity_widget.slider_released.connect(self.tree_widget.on_item_slider_released)
        self.intensity_widget.spin_box_changed.connect(self.tree_widget.on_item_spinbox_changed)

    def update(self):
        self.mode_widget.setMode(self.layer.mode)
        self.intensity_widget.set_intensity(self.layer.intensity)

    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        if column == 0:
            key1 = self.text(column)
            key2 = other.text(column)
        elif column == 1:
            key1 = self.text(column).lower()
            key2 = other.text(column).lower()
        elif column == 2:
            key1 = 4 if self.layer.mode == 1 else self.layer.mode
            key2 = 4 if other.layer.mode == 1 else other.layer.mode
            return key1 < key2
        elif column == 3:
            return self.layer.intensity < other.layer.intensity

        return self.natural_sort_key(key1) < self.natural_sort_key(key2)

    def __eq__(self, other):
        return self.layer == other.layer

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
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        column_names = ['#', 'Layer Name', 'Mode', 'Intensity']
        self.setColumnCount(len(column_names))
        self.setHeaderLabels(column_names)
        # self.setHeaderHidden(True)
        self.setSelectionMode(self.SelectionMode.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.header().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Fixed)

        self.itemDict = {}
        self.current_item_recording = None

        self._selected_items = []
        self._selected_layers = []

    def onClose(self):
        self.mainUI.settings['layerViewColumn'] = self.getColumnsWidth()

    def onShow(self):
        if 'layerViewColumn' in self.mainUI.settings:
            self.setColumnsWidth(self.mainUI.settings['layerViewColumn'])
            # space for scroll bar
            self.updateColumnSize(self.width()-20)

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

    def build(self, text, mode):
        self.itemDict.clear()
        self.clear()

        if self.mainUI.layers:
            for layer in self.mainUI.layers:
                if text in layer.name.lower() and is_valid_mode(layer.mode, mode):
                    item = ZlmTreeWidgetItem(self, layer)
                    l = self.itemDict.get(layer.name, [])
                    l.append(item)
                    self.itemDict[layer.name] = l

    def on_item_mode_changed(self, item, mode):
        column = self.sortColumn()
        if column == 2:
            self.setSortingEnabled(False)

        if mode == ZlmLayerMode.record:
            if self.current_item_recording:
                self.current_item_recording.layer.mode = ZlmLayerMode.active
                # current item recording might be deleted if filter was used
                try:
                    self.current_item_recording.mode_widget.setMode(ZlmLayerMode.active)
                except:
                    pass
            self.current_item_recording = item
            item.layer.mode = mode
        else:
            selectedItems = self.selectedItems()
            if selectedItems:
                for i in selectedItems:
                    if self.current_item_recording and self.current_item_recording == i:
                        self.current_item_recording = None
                    i.layer.mode = mode
                    i.mode_widget.setMode(mode)
            item.layer.mode = mode
            if self.current_item_recording and self.current_item_recording == item:
                self.current_item_recording = None

        if column == 2:
            self.setSortingEnabled(True)
            self.sortByColumn(column)

        send_to_zbrush()

    def on_item_slider_pressed(self, item, value):
        value = round(value, 2)
        if value < 0.000001:
            value = 0
        if value > 1.0:
            value = 1.0

        self._selected_items = self.selectedItems()
        self._selected_layers = [i.layer for i in self._selected_items]

        try:
            self._selected_items.remove(item)
        except Exception as e:
            self._selected_layers.append(item.layer)

        for i in self._selected_items:
            i.intensity_widget.set_intensity(value)

        for l in self._selected_layers:
            l.intensity = value

        # If there is an item recording deactivate it for now
        if self.current_item_recording:
            self.current_item_recording.layer.mode = ZlmLayerMode.active

        send_to_zbrush()

    def on_item_slider_released(self, item, value):
        value = round(value, 2)
        if value < 0.000001:
            value = 0
        if value > 1.0:
            value = 1.0

        # If there is an item recording deactivate it for now
        if self.current_item_recording:
            self.current_item_recording.layer.mode = ZlmLayerMode.record

        for l in self._selected_layers:
            l.intensity = value

        send_to_zbrush()

    def on_item_slider_moved(self, item, value):
        value = round(value, 2)
        if value < 0.01:
            # to keep the layer active and avoid a lag when scrubbing to zero
            # and scrubbing back to higher value
            value = 0.01
        if value > 1.0:
            value = 1.0
        send_intensity(self._selected_layers, value)
        for i in self._selected_items:
            i.intensity_widget.set_intensity(value)
            i.layer.intensity = value
        item.layer.itensity = value

    def on_item_spinbox_changed(self, item, value):
        value = round(value, 2)
        mode = ZlmLayerMode.active
        if value < 0.000001:
            value = 0
            mode = ZlmLayerMode.off
        if value > 1.0:
            value = 1.0
            mode = ZlmLayerMode.active

        if self.current_item_recording:
            self.current_item_recording.layer.mode = ZlmLayerMode.active
            self.current_item_recording = None

        for i in self.selectedItems():
            if i.layer != item.layer:
                i.intensity_widget.set_intensity(value)
                i.mode_widget.setMode(mode)
                i.layer.intensity = value
                i.layer.mode = mode

        item.layer.intensity = value
        item.layer.mode = mode
        item.mode_widget.setMode(mode)

        send_to_zbrush()

    def mousePressEvent(self, event):
        # https://stackoverflow.com/questions/2761284/is-it-possible-to-deselect-in-a-qtreeview-by-clicking-off-an-item
        item = self.itemAt(event.pos())
        if item and self.isItemSelected(item):
            self.setItemSelected(item, False)
        else:
            QtWidgets.QTreeWidget.mousePressEvent(self, event)

    def update_layer(self):
        column = self.sortColumn()
        self.setSortingEnabled(False)
        for key, layers in self.itemDict.items():
            for item in layers:
                item.update()
        self.setSortingEnabled(True)
        self.sortByColumn(column)

    def get_selected_layers(self):
        return [i.layer for i in self.selectedItems()]

    def get_recording_layer(self):
        if self.current_item_recording:
            return self.current_item_recording.layer
        return None

    def get_active_layers(self):
        layers = []

        for lays in self.itemDict.values():
            for l in lays:
                if l.layer.mode != 0:
                    layers.append(l.layer)

        return layers

    def updateColumnSize(self, width):
        width -= (self.columnWidth(0) + self.columnWidth(1) + self.columnWidth(2))

        if width < 60:
            width = 60
        self.setColumnWidth(3, width)

    def resizeEvent(self, event):
        width = event.size().width()

        self.updateColumnSize(width)