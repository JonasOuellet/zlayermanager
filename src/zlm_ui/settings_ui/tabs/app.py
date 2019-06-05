from PyQt5 import Qt, QtCore

from zlm_settings import ZlmSettings
from zlm_ui.settings_ui.base_setting_ui import SettingsTabBase, register_setting_tab


AVAILABLE_OUTPUT_FORMAT = ['.obj', '.fbx', '.ma', '.GoZ']


class ExportFormatDelegate(Qt.QStyledItemDelegate):
    def __init__(self, parent=None):
        Qt.QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = Qt.QComboBox(parent)
        editor.addItems(AVAILABLE_OUTPUT_FORMAT)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        try:
            editor.setCurrentIndex(AVAILABLE_OUTPUT_FORMAT.index(value))
        except:
            pass

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class AppSettingWidget(SettingsTabBase):

    columns = ('Application', 'Port', 'Format')
    columns_count = 3

    def __init__(self):
        SettingsTabBase.__init__(self, "External Application")

        self.pb_send_after_export = Qt.QPushButton('Send to app')
        self.pb_send_after_export.setCheckable(True)

        self.cb_current_app = Qt.QComboBox()

        self.app_table = Qt.QTableWidget()
        self.app_table.itemChanged.connect(self.item_changed)

        pb_add = Qt.QPushButton(Qt.QIcon(":/add.png"), '')
        pb_add.clicked.connect(self.add_app)
        pb_rem = Qt.QPushButton(Qt.QIcon(":/remove.png"), '')
        pb_rem.clicked.connect(self.remove_app)

        pb_reset = Qt.QPushButton(Qt.QIcon(":/reset.png"), "")
        pb_reset.clicked.connect(self.reset_settings)

        top_layout = Qt.QHBoxLayout()
        top_layout.addWidget(self.pb_send_after_export, 1)
        top_layout.addSpacing(10)
        top_layout.addWidget(Qt.QLabel("Current Application: "), 0)
        top_layout.addWidget(self.cb_current_app, 1)

        bot_layout = Qt.QHBoxLayout()
        bot_layout.addWidget(pb_add)
        bot_layout.addWidget(pb_rem)
        bot_layout.addStretch()
        bot_layout.addWidget(pb_reset)

        layout = Qt.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.app_table)
        layout.addLayout(bot_layout)

        self.set_layout(layout)

    def set_column_size(self):
        ratios = (0.5, 0.25, 0.25)

        availabed_width = self.app_table.size().width()
        for i in range(self.columns_count):
            self.app_table.setColumnWidth(i, availabed_width * ratios[i])

    def build_table(self, settings):
        self.app_table.blockSignals(True)
        self.app_table.clear()

        self.app_table.setHorizontalScrollBarPolicy(Qt.Qt.ScrollBarAlwaysOff)
        self.app_table.setShowGrid(False)
        self.app_table.verticalHeader().setVisible(False)

        self.app_table.horizontalHeader().setSectionResizeMode(Qt.QHeaderView.ResizeMode.Fixed)

        self.app_table.setColumnCount(self.columns_count)
        self.app_table.setHorizontalHeaderLabels(self.columns)
        self.app_table.setRowCount(len(settings.app_settings))

        self.app_table.setItemDelegateForColumn(2, ExportFormatDelegate())

        for i, (key, value) in enumerate(settings.app_settings.items()):
            self._set_item(i, key, value['port'], value['format'])

        self.set_column_size()
        self.app_table.blockSignals(False)

        self.disable_widget()

    def resizeEvent(self, event):
        self.set_column_size()

    def _set_item(self, i, soft, port, ext):
        item = Qt.QTableWidgetItem()
        item.setData(Qt.Qt.EditRole, port)

        self.app_table.setItem(i, 0, Qt.QTableWidgetItem(soft))
        self.app_table.setItem(i, 1, item)
        self.app_table.setItem(i, 2, Qt.QTableWidgetItem(ext))

    def build_combobox(self, settings):
        current_index = self.cb_current_app.currentIndex()
        count = self.cb_current_app.count()
        current_item = self.cb_current_app.currentText()
        if not current_item:
            current_item = settings.current_app

        self.cb_current_app.clear()

        items = list(settings.app_settings.keys())

        self.cb_current_app.addItems(items)

        if count == self.cb_current_app.count():
            self.cb_current_app.setCurrentIndex(current_index)
        else:
            try:
                self.cb_current_app.setCurrentIndex(items.index(current_item))
            except:
                pass

    def get_app_data(self, row_index):
        soft_name = self.app_table.item(row_index, 0).text()
        port = self.app_table.item(row_index, 1).data(Qt.Qt.EditRole)
        ext = self.app_table.item(row_index, 2).text()
        return soft_name, port, ext

    def get_app_table_data(self, check_error=False):
        out = {}
        for i in range(self.app_table.rowCount()):
            soft, port, ext = self.get_app_data(i)
            if check_error:
                if soft in out:
                    raise Exception('Application "{}" is dupplicated.'.format(soft))
            out[soft] = {
                'port': port,
                'format': ext
            }
        return out

    def update_cb_app(self):
        setting = ZlmSettings(False)
        self.save(setting)
        self.build_combobox(setting)

    def reset_settings(self):
        self.pb_send_after_export.setChecked(self.DEFAULT_SETTINGS.send_after_export)
        self.build_table(self.DEFAULT_SETTINGS)
        self.build_combobox(self.DEFAULT_SETTINGS)

    def add_app(self):
        self.app_table.blockSignals(True)
        count = self.app_table.rowCount()
        port = None
        name = 'application'
        index = 0
        for i in range(count):
            cp = self.app_table.item(i, 1).data(Qt.Qt.EditRole)
            if port is None:
                port = cp + 1
            elif cp == port:
                port += 1

            if self.app_table.item(i, 0).text().lower() == name:
                index += 1
                name = "application{:02d}".format(index)
        if port is None:
            port = 6009
        self.app_table.setRowCount(count + 1)
        self._set_item(count, name, port, AVAILABLE_OUTPUT_FORMAT[0])

        self.update_cb_app()
        self.app_table.blockSignals(False)

        self.disable_widget()

    def remove_app(self):
        rows = set()
        for item in self.app_table.selectedItems():
            rows.add(item.row())

        self.app_table.blockSignals(True)
        for row in reversed(list(rows)):
            self.app_table.removeRow(row)

        self.disable_widget()
        self.app_table.blockSignals(False)
        self.update_cb_app()
        self.cb_current_app.clear()

    def item_changed(self, item):
        if item.column() == 0:
            self.update_cb_app()

    def disable_widget(self):
        if self.app_table.rowCount() == 0:
            self.pb_send_after_export.setEnabled(False)
            self.cb_current_app.setEnabled(False)
        else:
            self.pb_send_after_export.setEnabled(True)
            self.cb_current_app.setEnabled(True)

    #
    # Base class method
    #

    def on_show(self):
        self.set_column_size()

    def on_close(self):
        pass

    def validate(self, settings):
        # make sure that no port is the same as default com port
        for soft, value in settings.app_settings.items():
            if value['port'] == settings.communication_port:
                return False, 'Error "{}" port cannot be the same as core port "{}".'.format(soft, settings.communication_port)
        return True, ""

    def save(self, settings):
        settings.send_after_export = self.pb_send_after_export.isChecked()
        settings.current_app = self.cb_current_app.currentText()

        data = self.get_app_table_data(check_error=True)
        # clear or not before ?
        settings.app_settings.clear()
        settings.app_settings.update(data)

    def update(self, settings):
        self.pb_send_after_export.setChecked(settings.send_after_export)
        self.build_table(settings)
        self.build_combobox(settings)


register_setting_tab(AppSettingWidget)
