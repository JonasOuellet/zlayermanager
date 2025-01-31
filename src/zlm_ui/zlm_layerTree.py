from typing import TYPE_CHECKING
import re
import math

from PyQt5 import QtWidgets, QtCore, QtGui

from zlm_core import ZlmLayerMode, ZlmLayer, main_layers
from zlm_ui.filter_widget import is_valid_mode
from zlm_to_zbrush import send_to_zbrush, send_intensity
from zlm_ui import layer_edit_option


if TYPE_CHECKING:
    from zlm_ui.main_ui import ZlmMainUI


MINIMUM_INTENSITY_WIDTH = 160


# Use delegate to make it faster ?
# https://stackoverflow.com/questions/7175333/how-to-create-delegate-for-qtreewidget

class NoWheelSlider(QtWidgets.QSlider):
    def __init__(self):
        QtWidgets.QSlider.__init__(self, QtCore.Qt.Orientation.Horizontal)

    def wheelEvent(self, event):
        pass


class ZlmIntensity(QtWidgets.QWidget):
    slider_pressed = QtCore.pyqtSignal(object, float)
    slider_released = QtCore.pyqtSignal(object, float)
    slider_moved = QtCore.pyqtSignal(object, float)

    spin_box_changed = QtCore.pyqtSignal(object, float)

    def __init__(self, item, allow_inverse_intensity: bool):
        super().__init__()
        self.item = item

        self.slider = NoWheelSlider()

        self.spinBox = QtWidgets.QDoubleSpinBox()
        self.spinBox.setSingleStep(0.1)

        self.update_range(allow_inverse_intensity)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.spinBox)

        self.setLayout(layout)

        self.slider.sliderMoved.connect(self._sliderMoved)
        self.slider.sliderPressed.connect(self._slider_pressed)
        self.slider.sliderReleased.connect(self._slider_released)
        self.spinBox.valueChanged.connect(self._spinBoxChanged)

        self.setMinimumWidth(MINIMUM_INTENSITY_WIDTH)

    def update_range(self, allow_bellow_zero: bool):
        if allow_bellow_zero:
            self.spinBox.setRange(-1, 1.0)
            self.slider.setRange(-100, 100)
        else:
            self.spinBox.setRange(0, 1.0)
            self.slider.setRange(0, 100)

    def set_intensity(self, value: float):
        self.spinBox.blockSignals(True)
        self.slider.setValue(round(value * 100))
        self.spinBox.setValue(value)
        self.spinBox.blockSignals(False)

    def _sliderMoved(self, value: int):
        f_value = value / 100.0
        self.spinBox.blockSignals(True)
        self.spinBox.setValue(f_value)
        self.spinBox.blockSignals(False)

        self.slider_moved.emit(self.item, f_value)

    def _spinBoxChanged(self, value: float):
        self.slider.setValue(round(value * 100))
        self.spin_box_changed.emit(self.item, value)

    def _slider_pressed(self):
        self.slider_pressed.emit(self.item, self.spinBox.value())

    def _slider_released(self):
        self.slider_released.emit(self.item, self.spinBox.value())


class ZlmModeWidget(QtWidgets.QWidget):
    mode_changed = QtCore.pyqtSignal(object, object)

    def __init__(self, item, mode=ZlmLayerMode.off):
        QtWidgets.QWidget.__init__(self)

        self.item = item

        layout = QtWidgets.QHBoxLayout()
        self.pb_on = QtWidgets.QPushButton(QtGui.QIcon(":/eye.png"), "")
        self.pb_on.setCheckable(True)
        self.pb_on.setMaximumSize(QtCore.QSize(32, 32))
        self.pb_rect = QtWidgets.QPushButton(QtGui.QIcon(":/record.png"), "")
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
    def __init__(
        self,
        parent: "ZlmLayerTreeWidget",
        layer: ZlmLayer | None = None,
        allow_inverse_intensity: bool = False
    ):
        super().__init__(parent)
        self.tree_widget = parent
        self.layer = layer

        self.mode_widget = ZlmModeWidget(self)
        self.intensity_widget = ZlmIntensity(self, allow_inverse_intensity)

        if self.layer:
            self.update()

        self.tree_widget.setItemWidget(self, 2, self.mode_widget)
        self.tree_widget.setItemWidget(self, 3, self.intensity_widget)

        self.mode_widget.mode_changed.connect(self.tree_widget.on_item_mode_changed)
        self.intensity_widget.slider_pressed.connect(self.tree_widget.on_item_slider_pressed)
        self.intensity_widget.slider_moved.connect(self.tree_widget.on_item_slider_moved)
        self.intensity_widget.slider_released.connect(self.tree_widget.on_item_slider_released)
        self.intensity_widget.spin_box_changed.connect(self.tree_widget.on_item_spinbox_changed)

    def update(self):
        self.setText(0, str(self.layer.index))
        self.setText(1, self.layer.name)
        self.mode_widget.setMode(self.layer.mode)
        self.intensity_widget.set_intensity(self.layer.intensity)

    def __lt__(self, other: "ZlmTreeWidgetItem"):
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

    def __eq__(self, other: "ZlmTreeWidgetItem"):
        return self.layer == other.layer

    @staticmethod
    def natural_sort_key(key):
        regex = r'(\d*\.\d+|\d+)'
        parts = re.split(regex, key)
        return tuple((e if i % 2 == 0 else float(e)) for i, e in enumerate(parts))


def prog_column_resizing(func):
    def wrapper(self, *args, **kwargs):
        self._is_resizing = True
        to_return = func(self, *args, **kwargs)
        self._is_resizing = False
        return to_return
    return wrapper


class ZlmLayerTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent: "ZlmMainUI"):
        super().__init__(parent)
        self.main_ui = parent
        self.main_ui.closing.connect(self.on_close)
        self.main_ui.showing.connect(self.on_show)

        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)
        column_names = ['#', 'Layer Name', 'Mode', 'Intensity']
        self.setColumnCount(len(column_names))
        self.setHeaderLabels(column_names)
        self.setSelectionMode(self.SelectionMode.ExtendedSelection)

        self.header().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        # column resizing
        self._is_resizing = False
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.header().sectionResized.connect(self.columnResized)

        self.itemDict: dict[str, list[ZlmTreeWidgetItem]] = {}
        self.current_item_recording = None

        self._selected_items: list[ZlmTreeWidgetItem] = []
        self._selected_layers: list[ZlmLayer] = []

        self.filter_text = ''
        self.filter_mode = 0

        self.installEventFilter(self)

        self.main_ui.settings_changed.connect(self.on_settings_changed)

    def on_settings_changed(self):
        self.update_widget_range()

    def update_widget_range(self):
        set_bellow_zero = layer_edit_option.should_go_bellow_zero()
        for idx in range(self.topLevelItemCount()):
            item: ZlmTreeWidgetItem = self.topLevelItem(idx)
            item.intensity_widget.update_range(set_bellow_zero)

    def on_close(self):
        self.main_ui.settings['layerViewColumn'] = self.getColumnsWidth()

    def on_show(self):
        if 'layerViewColumn' in self.main_ui.settings:
            self.setColumnsWidth(self.main_ui.settings['layerViewColumn'])
            # space for scroll bar
            self.updateColumnSize(self.width())

    def getColumnsWidth(self):
        columnCount = self.columnCount()
        columnWidth = [60] * columnCount
        for x in range(columnCount):
            columnWidth[x] = self.columnWidth(x)

        return columnWidth

    @prog_column_resizing
    def setColumnsWidth(self, width):
        # Set column With:
        for x, w in enumerate(width):
            if x < self.columnCount():
                self.setColumnWidth(x, w)

    def set_record_layer(self, layer: "ZlmLayer"):
        layer.mode = ZlmLayerMode.record
        if self.current_item_recording:
            # current item recording might be deleted if filter was used
            try:
                self.current_item_recording.mode_widget.setMode(ZlmLayerMode.active)
            except:
                pass

        item = self.item_for_layer(layer)
        if item:
            self.current_item_recording = item

    def on_item_mode_changed(self, item, mode):
        column = self.sortColumn()
        if column == 2:
            order = self.header().sortIndicatorOrder()
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
            self.sortByColumn(column, order)

        send_to_zbrush()

    def on_item_slider_pressed(self, item: ZlmTreeWidgetItem, value: float):
        value = round(value, 2)
        if value < 0.000001:
            value = 0
        if value > 1.0:
            value = 1.0

        self._selected_items = self.selectedItems()
        self._selected_layers = [i.layer for i in self._selected_items]

        try:
            self._selected_items.remove(item)
        except:
            self._selected_layers.append(item.layer)

        for i in self._selected_items:
            i.intensity_widget.set_intensity(value)

        for layer in self._selected_layers:
            layer.intensity = value

        # If there is an item recording deactivate it for now
        if self.current_item_recording:
            self.current_item_recording.layer.mode = ZlmLayerMode.active

        send_to_zbrush()

    def on_item_slider_released(self, item, value):
        value = round(value, 2)
        should_disable = math.isclose(value, 0.0, abs_tol=1e-9)

        # If there was an item recording reactivate it
        record_layer = None
        if self.current_item_recording:
            record_layer = self.current_item_recording.layer
            record_layer.mode = ZlmLayerMode.record

        for layer in self._selected_layers:
            layer.intensity = value
            if should_disable:
                layer.mode = ZlmLayerMode.off
                if item := self.item_for_layer(layer):
                    item.update()
            else:
                if layer != record_layer:
                    layer.mode = ZlmLayerMode.active
                    if item := self.item_for_layer(layer):
                        item.update()
        send_to_zbrush()

    def on_item_slider_moved(self, item: ZlmTreeWidgetItem, value: float):
        value = round(value, 2)
        for i in self._selected_items:
            i.intensity_widget.set_intensity(value)
            i.layer.intensity = value
        item.layer.intensity = value

        send_intensity(self._selected_layers)

    def on_item_spinbox_changed(self, item: ZlmTreeWidgetItem, value: float):
        value = round(value, 2)
        should_disable = math.isclose(value, 0.0, abs_tol=1e-9)

        record_layer = None
        if self.current_item_recording:
            record_layer = self.current_item_recording.layer
            record_layer.mode = ZlmLayerMode.record

        mode = ZlmLayerMode.off if should_disable else ZlmLayerMode.active

        selectedItems: list[ZlmTreeWidgetItem] = self.selectedItems()
        for i in selectedItems:
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
        # do nothing if right click button ??
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            return
        item = self.itemAt(event.pos())
        item_selected = len(self.selectedItems())
        if item and item_selected == 1 and item.isSelected() and event.button() != QtCore.Qt.MouseButton.RightButton:
            item.setSelected(False)
        else:
            QtWidgets.QTreeWidget.mousePressEvent(self, event)

    def should_be_visible(self, layer: ZlmLayer):
        return self.filter_text in layer.name.lower() and is_valid_mode(layer.mode, self.filter_mode)

    def create_layer(self, layer: ZlmLayer, allow_inverse_intensity: bool = False):
        if self.should_be_visible(layer):
            item = ZlmTreeWidgetItem(self, layer, allow_inverse_intensity)
            layers = self.itemDict.get(layer.name, [])
            layers.append(item)
            self.itemDict[layer.name] = layers

        if layer.mode == ZlmLayerMode.record:
            self.set_record_layer(layer)

    def build(self, text, mode):
        self.itemDict.clear()
        self.clear()

        self.filter_text = text
        self.filter_mode = mode

        set_bellow_zero = layer_edit_option.should_go_bellow_zero()

        for layer in main_layers.instances_list:
            self.create_layer(layer, set_bellow_zero)
        self.updateColumnSize()

    def update_layer(self):
        column = self.sortColumn()
        order = self.header().sortIndicatorOrder()

        self.current_item_recording = None
        self.setSortingEnabled(False)
        for key, layers in self.itemDict.items():
            for item in layers:
                item.update()

                if item.layer.mode == ZlmLayerMode.record:
                    self.current_item_recording = item

        self.setSortingEnabled(True)
        self.sortByColumn(column, order)

    def layer_created(self, layer):
        self.create_layer(layer)

    def layer_removed(self, layer):
        item = self.item_for_layer(layer)
        if item:
            if self.current_item_recording and self.current_item_recording == item:
                self.current_item_recording = None

            index = self.indexOfTopLevelItem(item)
            self.takeTopLevelItem(index)

            self.itemDict[layer.name].remove(item)

        self.update_layer()

    def layer_renamed(self, layer: ZlmLayer, old_name: str):
        item = None
        items = self.itemDict.get(old_name, None)
        if items:
            if len(items) == 1:
                item = items[0]
            else:
                for i in items:
                    if i.layer == layer:
                        item = i
                        break
        if item:
            items.remove(item)

            if self.should_be_visible(layer):
                layers = self.itemDict.get(layer.name, [])
                layers.append(item)
                self.itemDict[layer.name] = layers

                column = self.sortColumn()
                if column == 1:
                    order = self.header().sortIndicatorOrder()
                    self.setSortingEnabled(False)

                item.update()

                if column == 1:
                    self.setSortingEnabled(True)
                    self.sortByColumn(column, order)
            else:
                index = self.indexOfTopLevelItem(item)
                self.takeTopLevelItem(index)

    def get_recording_layer(self):
        if self.current_item_recording:
            return self.current_item_recording.layer
        return None

    def get_active_layers(self):
        out: list[ZlmLayer] = []

        for layers in self.itemDict.values():
            for layer in layers:
                if layer.layer.mode != 0:
                    layers.append(layer.layer)
        return out

    @prog_column_resizing
    def updateColumnSize(self, width=None):
        if width is None:
            width = self.width()

        if self.verticalScrollBar().isVisible():
            width -= self.verticalScrollBar().width()

        width -= (self.columnWidth(0) + self.columnWidth(1) + self.columnWidth(2))

        valid = True
        if width < MINIMUM_INTENSITY_WIDTH:
            width = MINIMUM_INTENSITY_WIDTH
            valid = False
        self.setColumnWidth(3, width)
        return valid

    def resizeEvent(self, event):
        width = event.size().width()

        self.updateColumnSize(width)

    def columnResized(self, column, oldSize, newSize):
        if not self._is_resizing and column != 3:
            if not self.updateColumnSize():
                self._is_resizing = True
                self.setColumnWidth(column, oldSize)
                self._is_resizing = False

    def has_item_selected(self):
        return len(self.selectedItems()) > 0

    def get_item_under_mouse(self) -> ZlmTreeWidgetItem | None:
        pos = self.viewport().mapFromGlobal(QtGui.QCursor.pos())
        item = self.itemAt(pos)
        if item:
            return item
        return None

    def get_layer_under_mouse(self):
        item = self.get_item_under_mouse()
        if item:
            return item.layer
        return None

    def get_selected_layers(self, include_under_mouse=False):
        sel = [i.layer for i in self.selectedItems()]
        if include_under_mouse:
            item = self.get_item_under_mouse()
            if item and item.layer not in sel:
                sel.append(item.layer)
        return sel

    def item_for_layer(self, layer: ZlmLayer) -> ZlmTreeWidgetItem | None:
        items = self.itemDict.get(layer.name, None)
        if items:
            if len(items) == 1:
                return items[0]
            else:
                for item in items:
                    if item.layer == layer:
                        return item
        return None

    def invert_selection(self):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            item.setSelected(not item.isSelected())

    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.Type.KeyPress:
            if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
                key = event.key()
                if key == QtCore.Qt.Key.Key_I:
                    self.invert_selection()
                    return True
                if key == QtCore.Qt.Key.Key_A:
                    self.selectAll()
                    return True
                if key == QtCore.Qt.Key.Key_X:
                    self.clearSelection()
                    return True
        return QtWidgets.QTreeWidget.eventFilter(self, widget, event)
