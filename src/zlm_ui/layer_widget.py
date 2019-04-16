from PySide2 import QtWidgets, QtCore

from zlm_settings import ZlmSettings
import zlm_core
from zlm_ui.zlm_layertree import ZlmLayerTreeWidget
from zlm_ui.filter_widget import LayerFilterWidget
from zlm_ui.preset_widget import ZlmPresetWidget
from zlm_ui.export_widget import ZlmExportWidget


class ZlmLayerWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.preset_widget = ZlmPresetWidget()
        self.filter_widget = LayerFilterWidget(parent)
        self.tree_widget = ZlmLayerTreeWidget(parent)
        self.tree_widget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.tree_widget_custom_menu)

        self.filter_widget.filter_edited.connect(self.tree_widget.build)
        self.preset_widget.preset_changed.connect(self.tree_widget.update_layer)

        self.export_widget = ZlmExportWidget()
        self.export_widget.pb_all.clicked.connect(self.export_all)
        self.export_widget.pb_sel.clicked.connect(self.export_selected)
        self.export_widget.pb_active.clicked.connect(self.export_active)
        self.export_widget.pb_record.clicked.connect(self.export_record)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.preset_widget)
        layout.addWidget(self.filter_widget)
        layout.addWidget(self.tree_widget)
        layout.addWidget(self.export_widget)

        self.setLayout(layout)

    def build(self):
        self.tree_widget.build(self.filter_widget.le_search_bar.text(), self.filter_widget.current_filter)

    def export_all(self):
        settings = ZlmSettings.instance()

        zlm_core.export_layers(settings.get_export_folder(), settings.export_format, maya_auto_import=settings.maya_auto_import)

    def export_selected(self):
        settings = ZlmSettings.instance()
        layers = self.tree_widget.get_selected_layers()
        if layers:
            zlm_core.export_layers(settings.get_export_folder(), settings.export_format, layers, maya_auto_import=settings.maya_auto_import)

    def export_active(self):
        settings = ZlmSettings.instance()
        layers = self.tree_widget.get_active_layers()
        if layers:
            zlm_core.export_layers(settings.get_export_folder(), settings.export_format, layers, maya_auto_import=settings.maya_auto_import)

    def export_record(self):
        settings = ZlmSettings.instance()
        layer = self.tree_widget.get_recording_layer()
        if layer:
            zlm_core.export_layers(settings.get_export_folder(), settings.export_format, [layer], maya_auto_import=settings.maya_auto_import)

    def tree_widget_custom_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        turn_off_action = QtWidgets.QAction('Turn All Off', self)
        turn_off_action.triggered.connect(self.turn_all_off)

        menu.addAction(turn_off_action)
        menu.popup(self.tree_widget.mapToGlobal(pos))

    def turn_all_off(self):
        for layer in zlm_core._zOp.instances_list:
            layer.mode = 0
        self.tree_widget.update_layer()
        zlm_core.send_to_zbrush()
