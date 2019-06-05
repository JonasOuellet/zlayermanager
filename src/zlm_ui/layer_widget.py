from PyQt5 import Qt

import zlm_core
from zlm_settings import ZlmSettings
from zlm_to_zbrush import (
    export_layers, create_layer, send_to_zbrush, send_deleted_layers,
    send_new_layers_name, send_duplicated_layers, send_merged_layers
)
from zlm_ui.zlm_layertree import ZlmLayerTreeWidget
from zlm_ui.filter_widget import LayerFilterWidget
from zlm_ui.preset_widget import ZlmPresetWidget
from zlm_ui.export_widget import ZlmExportWidget
from zlm_ui.import_widget import ZlmImportWidget
from zlm_ui import layer_edit_option as leo
from zlm_ui.rename_dialog import RenameDialog


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
        zlm_core.main_layers.add_callback(zlm_core.ZlmLayers.cb_layer_renamed, self.tree_widget.layer_renamed)
        zlm_core.main_layers.add_callback(zlm_core.ZlmLayers.cb_layers_changed, self.tree_widget.update_layer)

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
        turn_off_action = Qt.QAction(Qt.QIcon(":/eye.png"), 'Turn All Off', self)
        turn_off_action.triggered.connect(self.turn_all_off)

        create_action = Qt.QAction(Qt.QIcon(':/add.png'), 'Create Layer', self)
        create_action.triggered.connect(self.create_layer)

        selected_layers = self.tree_widget.get_selected_layers()
        layer_under_mouse = self.tree_widget.get_layer_under_mouse()
        suff = 's' if len(selected_layers) > 1 else ''
        if selected_layers:
            remove_action = Qt.QAction(Qt.QIcon(':/remove.png'), f'Delete selected layer{suff}', self)
            remove_action.triggered.connect(lambda: self.remove_layer(selected_layers))

            duplicate_action = Qt.QAction(Qt.QIcon(':/duplicate.png'), f'Duplicate selected layer{suff}', self)
            duplicate_action.triggered.connect(lambda: self.duplicate_layer(selected_layers))

        if len(selected_layers) > 1:
            merge_action = Qt.QAction(Qt.QIcon(":/merge.png"), "Merge selected layers", self)
            merge_action.triggered.connect(lambda: self.merge_layers(selected_layers))

        rename_icon = Qt.QIcon(':/rename.png')

        remove_name_dup = Qt.QAction(rename_icon, 'Fix up layers name', self)
        remove_name_dup.triggered.connect(self.remove_name_dup)

        if layer_under_mouse:
            rename_action = Qt.QAction(rename_icon, 'Rename layer', self)
            rename_action.triggered.connect(lambda: self.rename_layer(layer_under_mouse))

        if len(selected_layers) > 1:
            bulk_rename = Qt.QAction(rename_icon, f'Rename selected layers', self)
            bulk_rename.triggered.connect(lambda: self.bulk_rename(selected_layers))

        menu.addAction(turn_off_action)
        menu.addSeparator()
        menu.addAction(create_action)

        if selected_layers:
            menu.addAction(remove_action)
            menu.addAction(duplicate_action)

        if len(selected_layers) > 1:
            menu.addAction(merge_action)

        menu.addSeparator()

        if layer_under_mouse:
            menu.addAction(rename_action)
        if len(selected_layers) > 1:
            menu.addAction(bulk_rename)

        menu.addAction(remove_name_dup)

        menu.popup(self.tree_widget.mapToGlobal(pos))

    def turn_all_off(self):
        for layer in zlm_core.main_layers.instances_list:
            layer.mode = 0
        self.tree_widget.update_layer()
        send_to_zbrush()

    def create_layer(self):
        validated_name = zlm_core.main_layers.validate_layer_name('newLayer00')
        text = self._get_name_("Layer Name", "New layer name: ", validated_name)
        if text:
            validated_name = zlm_core.main_layers.validate_layer_name(text)
            layer = zlm_core.main_layers.create_layer(validated_name, zlm_core.ZlmLayerMode.record)

            # focus newly created layer
            self.tree_widget.clearSelection()
            item = self.tree_widget.item_for_layer(layer)
            if item:
                self.tree_widget.scrollToItem(item)

            # send to zbrush:
            create_layer(layer)

    def remove_layer(self, layers):
        result = True
        if leo.should_ask_before_delete():
            result = Qt.QMessageBox.warning(self, "Delete Layers", 'This will delete selected layers.  Are you sure?',
                                            Qt.QMessageBox.StandardButton.Yes, Qt.QMessageBox.StandardButton.No)
            result = result == Qt.QMessageBox.StandardButton.Yes

        if result:
            for layer in layers:
                zlm_core.main_layers.remove_layer(layer)
            send_deleted_layers(layers)

    def duplicate_layer(self, layers):
        dup_layers = []
        move_dup_down = leo.should_move_dup_down()
        for layer in layers:
            dup_layers.append(zlm_core.main_layers.duplicate_layer(layer, move_dup_down))

        self.tree_widget.clearSelection()
        for _, target in dup_layers:
            item = self.tree_widget.item_for_layer(target)
            if item:
                item.setSelected(True)

        # focus newly created layer
        item = self.tree_widget.item_for_layer(dup_layers[-1][1])
        if item:
            self.tree_widget.scrollToItem(item)

        send_duplicated_layers(dup_layers, move_dup_down)

    def merge_layers(self, layers):
        zlm_core.main_layers.merge_layers(layers)
        send_merged_layers(layers)

    def rename_layer(self, layer):
        text = self._get_name_("Layer Name", "Layer name: ", layer.name)
        if text:
            if zlm_core.main_layers.rename_layer(layer, text):
                send_new_layers_name(layer)

    def bulk_rename(self, layers):
        _, ex_name = zlm_core.main_layers.remove_invalid_char(layers[0].name)
        dialog = RenameDialog(ex_name, self)
        if dialog.exec_():
            names = [l.name for l in layers]
            new_names = dialog.rename(names)
            mod_layers = []
            for layer, new_name in zip(layers, new_names):
                if zlm_core.main_layers.rename_layer(layer, new_name):
                    mod_layers.append(layer)

            if mod_layers:
                send_new_layers_name(mod_layers)

    def remove_name_dup(self):
        layers = zlm_core.main_layers.fix_up_names()
        if layers:
            send_new_layers_name(layers)

    def on_close(self):
        self.main_ui.settings['import_collapsed'] = self.import_widget.is_collapsed()
        self.main_ui.settings['export_collapsed'] = self.export_widget.is_collapsed()
        self.main_ui.settings['preset_collapsed'] = self.preset_widget.is_collapsed()
        self.main_ui.settings['preset_path'] = self.preset_widget.get_current_preset_path()
        self.export_widget.on_close()

    def _get_name_(self, title='Enter Name', label='Name: ', text=''):
        dialog = Qt.QInputDialog(self)
        dialog.setInputMode(Qt.QInputDialog.InputMode.TextInput)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setTextValue(text)
        # https://forum.qt.io/topic/9171/solved-how-can-a-lineedit-accept-only-ascii-alphanumeric-character-required-a-z-a-z-0-9/4 
        lineEdit = dialog.findChild(Qt.QLineEdit)
        lineEdit.setValidator(Qt.QRegExpValidator(Qt.QRegExp(zlm_core.valid_name_re), dialog))
        if dialog.exec_():
            return dialog.textValue()
        return None
