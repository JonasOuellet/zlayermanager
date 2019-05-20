from PyQt5 import Qt, QtCore

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


class DccSettingWidget(SettingsTabBase):

    columns = ('Software', 'Port', 'Format')
    columns_count = 3

    def __init__(self):
        SettingsTabBase.__init__(self, "External Software")

        self.pb_send_after_export = Qt.QPushButton('Send After Export')
        self.pb_send_after_export.setCheckable(True)

        self.cb_current_dcc = Qt.QComboBox()

        self.dcc_table = Qt.QTableWidget()

        pb_add = Qt.QPushButton(Qt.QIcon(":/add.png"), '')
        pb_rem = Qt.QPushButton(Qt.QIcon(":/remove.png"), '')

        pb_reset = Qt.QPushButton(Qt.QIcon(":/reset.png"), "")

        top_layout = Qt.QHBoxLayout()
        top_layout.addWidget(self.pb_send_after_export, 1)
        top_layout.addSpacing(10)
        top_layout.addWidget(Qt.QLabel("Current Software: "), 0)
        top_layout.addWidget(self.cb_current_dcc, 1)

        bot_layout = Qt.QHBoxLayout()
        bot_layout.addWidget(pb_add)
        bot_layout.addWidget(pb_rem)
        bot_layout.addStretch()
        bot_layout.addWidget(pb_reset)

        layout = Qt.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.dcc_table)
        layout.addLayout(bot_layout)

        self.set_layout(layout)

    def set_column_size(self):
        ratios = (0.5, 0.25, 0.25)

        availabed_width = self.dcc_table.size().width()
        for i in range(self.columns_count):
            self.dcc_table.setColumnWidth(i, availabed_width * ratios[i])

    def build_table(self, settings):
        self.dcc_table.clear()

        self.dcc_table.setHorizontalScrollBarPolicy(Qt.Qt.ScrollBarAlwaysOff)
        self.dcc_table.setShowGrid(False)
        self.dcc_table.verticalHeader().setVisible(False)

        self.dcc_table.horizontalHeader().setSectionResizeMode(Qt.QHeaderView.ResizeMode.Fixed)

        self.dcc_table.setColumnCount(self.columns_count)
        self.dcc_table.setHorizontalHeaderLabels(self.columns)
        self.dcc_table.setRowCount(len(settings.dcc_settings))

        self.dcc_table.setItemDelegateForColumn(2, ExportFormatDelegate())

        for i, (key, value) in enumerate(settings.dcc_settings.items()):
            item = Qt.QTableWidgetItem()
            item.setData(Qt.Qt.EditRole, value['port'])

            self.dcc_table.setItem(i, 0, Qt.QTableWidgetItem(key))
            self.dcc_table.setItem(i, 1, item)
            self.dcc_table.setItem(i, 2, Qt.QTableWidgetItem(value['format']))

        self.set_column_size()

    def resizeEvent(self, event):
        self.set_column_size()

    def build_combobox(self, settings):
        current_item = self.cb_current_dcc.currentText()
        if not current_item:
            current_item = settings.current_dcc

        self.cb_current_dcc.clear()

        items = list(settings.dcc_settings.keys())

        self.cb_current_dcc.addItems(items)

        try:
            self.cb_current_dcc.setCurrentIndex(items.index(current_item))
        except:
            pass

    def get_software_data(self, row_index):
        soft_name = self.dcc_table.item(row_index, 0).text()
        port = self.dcc_table.item(row_index, 1).data(Qt.Qt.EditRole)
        ext = self.dcc_table.item(row_index, 2).text()
        return soft_name, port, ext

    def get_software_table_data(self, check_error=False):
        out = {}
        for i in range(self.dcc_table.rowCount()):
            soft, port, ext = self.get_software_data(i)
            if check_error:
                if soft in out:
                    raise Exception('Software "{}" is dupplicated.'.format(soft))
            out[soft] = {
                'port': port,
                'format': ext
            }
        return out
    #
    # Base class method
    #

    def on_show(self):
        self.set_column_size()

    def on_close(self):
        pass

    def validate(self, settings):
        # make sure that no port is the same as default com port
        for soft, value in settings.dcc_settings.items():
            if value['port'] == settings.communication_port:
                return False, 'Error "{}" port cannot be the same as core port "{}".'.format(soft, settings.communication_port)
        return True, ""

    def save(self, settings):
        settings.send_after_export = self.pb_send_after_export.isChecked()
        settings.current_dcc = self.cb_current_dcc.currentText()

        data = self.get_software_table_data(check_error=True)
        settings.dcc_settings.update(data)

    def update(self, settings):
        self.pb_send_after_export.setChecked(settings.send_after_export)
        self.build_table(settings)
        self.build_combobox(settings)


register_setting_tab(DccSettingWidget)
