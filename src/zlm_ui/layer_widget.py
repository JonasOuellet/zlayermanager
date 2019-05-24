from PyQt5 import Qt

import zlm_core
from zlm_settings import ZlmSettings
from zlm_to_zbrush import export_layers

from zlm_ui.zlm_layertree import ZlmLayerTreeWidget
from zlm_ui.filter_widget import LayerFilterWidget
from zlm_ui.preset_widget import ZlmPresetWidget
from zlm_ui.export_widget import ZlmExportWidget
from zlm_ui.import_widget import ZlmImportWidget


class ZlmLayerWidget(Qt.QWidget):
    def __init__(self, parent):
        Qt.QWidget.__init__(self, parent)

        self.main_ui = parent
        self.main_ui.closing.connect(self.on_close)

        self.preset_widget = ZlmPresetWidget()
        self.filter_widget = LayerFilterWidget(parent)
        self.tree_widget = ZlmLayerTreeWidget(parent)
        self.tree_widget.setContextMenuPolicy(Qt.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.tree_widget_custom_menu)

        self.filter_widget.filter_edited.connect(self.tree_widget.build)
        self.preset_widget.preset_activated.connect(self.tree_widget.update_layer)

        self.export_widget = ZlmExportWidget(self.main_ui)
        self.export_widget.pb_all.clicked.connect(self.export_all)
        self.export_widget.pb_sel.clicked.connect(self.export_selected)
        self.export_widget.pb_active.clicked.connect(self.export_active)
        self.export_widget.pb_record.clicked.connect(self.export_record)
        self.export_widget.pb_base.clicked.connect(self.export_base)

        self.import_widget = ZlmImportWidget(self.main_ui)

        layout = Qt.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.preset_widget)
        layout.addWidget(self.filter_widget)
        layout.addWidget(self.tree_widget)
        layout.addWidget(self.export_widget)
        layout.addWidget(self.import_widget)

        self.setLayout(layout)

        self.import_widget.set_collapsed(self.main_ui.settings.get('import_collapsed', False))
        self.export_widget.set_collapsed(self.main_ui.settings.get('export_collapsed', False))
        self.preset_widget.set_collapsed(self.main_ui.settings.get('preset_collapsed', False))
        self.preset_widget.set_current_preset_path(self.main_ui.settings.get('preset_path', None))

        zlm_core.main_layers.add_callback(zlm_core.ZlmLayers.cb_layer_created, self.tree_widget.layer_created)
        zlm_core.main_layers.add_callback(zlm_core.ZlmLayers.cb_layer_removed, self.tree_widget.layer_removed)
        zlm_core.main_layers.add_callback(zlm_core.ZlmLayers.cb_layer_updated, self.build)

    def build(self):
        self.tree_widget.build(self.filter_widget.le_search_bar.text(), self.filter_widget.current_filter)

    def export_all(self):
        export_layers(subdiv=self.export_widget.get_subdiv())

    def export_selected(self):
        layers = self.tree_widget.get_selected_layers()
        if layers:
            export_layers(layers, subdiv=self.export_widget.get_subdiv())

    def export_active(self):
        layers = self.tree_widget.get_active_layers()
        if layers:
            export_layers(layers, subdiv=self.export_widget.get_subdiv())

    def export_record(self):
        layer = self.tree_widget.get_recording_layer()
        if layer:
            export_layers([layer], subdiv=self.export_widget.get_subdiv())

    def export_base(self):
        export_layers([], base_mesh=True, subdiv=self.export_widget.get_subdiv())

    def tree_widget_custom_menu(self, pos):
        menu = Qt.QMenu(self)
        turn_off_action = Qt.QAction('Turn All Off', self)
        turn_off_action.triggered.connect(self.turn_all_off)

        menu.addAction(turn_off_action)
        menu.popup(self.tree_widget.mapToGlobal(pos))

    def turn_all_off(self):
        for layer in zlm_core._zOp.instances_list:
            layer.mode = 0
        self.tree_widget.update_layer()
        zlm_core.send_to_zbrush()

    def on_close(self):
        self.main_ui.settings['import_collapsed'] = self.import_widget.is_collapsed()
        self.main_ui.settings['export_collapsed'] = self.export_widget.is_collapsed()
        self.main_ui.settings['preset_collapsed'] = self.preset_widget.is_collapsed()
        self.main_ui.settings['preset_path'] = self.preset_widget.get_current_preset_path()
        self.export_widget.on_close()
