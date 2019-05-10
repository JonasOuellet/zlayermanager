from PyQt5 import Qt, QtCore

import zlm_settings
from zlm_ui.collapsable import ZlmCollapsableWidget


DEFAULT_SETTINGS = zlm_settings.ZlmSettings(False)


class CoreSettingWidget(ZlmCollapsableWidget):

    def __init__(self, collapsed=False):
        ZlmCollapsableWidget.__init__(self, "Core")

        self.settings = zlm_settings.ZlmSettings.instance()

        self.le_working_folder = Qt.QLineEdit()
        self.pb_working_browse = Qt.QPushButton(Qt.QIcon(":/folder.png"), "")
        self.pb_working_reset = Qt.QPushButton(Qt.QIcon(":/reset.png"), "")

        self.le_working_folder.setText(self.settings.working_folder)
        self.pb_working_browse.clicked.connect(self.browse_working_folder)
        self.pb_working_reset.clicked.connect(self.reset_working_folder)

        self.sb_com_port = Qt.QSpinBox()
        self.sb_com_port.setRange(1000, 9999)
        self.sb_com_port.setValue(self.settings.communication_port)

        self.pb_reset_port = Qt.QPushButton(Qt.QIcon(":/reset.png"), "")

        self.pb_reset_port.clicked.connect(self.reset_port)

        work_layout = Qt.QHBoxLayout()
        work_layout.addWidget(Qt.QLabel("File Folder: "), 0)
        work_layout.addWidget(self.le_working_folder, 1)
        work_layout.addWidget(self.pb_working_browse, 0)
        work_layout.addWidget(self.pb_working_reset, 0)

        port_layout = Qt.QHBoxLayout()
        port_layout.addStretch()
        port_layout.addWidget(Qt.QLabel("Port: "), 0)
        port_layout.addWidget(self.sb_com_port, 0)
        port_layout.addWidget(self.pb_reset_port, 0)

        layout = Qt.QVBoxLayout()
        layout.addLayout(work_layout)
        layout.addLayout(port_layout)

        self.content_widget.setLayout(layout)

        self.set_collapsed(collapsed)

    def browse_working_folder(self):
        directory = Qt.QFileDialog.getExistingDirectory(self, "Select file folder", self.settings.working_folder)
        if directory:
            self.le_working_folder.setText(directory)

    def accept_settings(self):
        self.settings.working_folder = self.le_working_folder.text()
        self.settings.communication_port = self.sb_com_port.value()

    def on_close(self):
        pass

    def reset_working_folder(self):
        self.le_working_folder.setText(DEFAULT_SETTINGS.working_folder)

    def reset_port(self):
        self.sb_com_port.setValue(DEFAULT_SETTINGS.communication_port)


class DccSettingWidget(ZlmCollapsableWidget):

    columns = ('Software', 'Port', 'Format')
    columns_count = 3

    def __init__(self, collapsed=False):
        ZlmCollapsableWidget.__init__(self, "External Software")

        self.settings = zlm_settings.ZlmSettings.instance()

        self.pb_send_after_export = Qt.QPushButton('Send After Export')
        self.pb_send_after_export.setCheckable(True)
        self.pb_send_after_export.setChecked(self.settings.send_after_export)

        self.cb_current_dcc = Qt.QComboBox()

        self.dcc_table = Qt.QTableWidget()

        top_layout = Qt.QHBoxLayout()
        top_layout.addWidget(self.pb_send_after_export, 1)
        top_layout.addSpacing(10)
        top_layout.addWidget(Qt.QLabel("Current Soft: "), 0)
        top_layout.addWidget(self.cb_current_dcc, 1)

        layout = Qt.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.dcc_table)

        self.content_widget.setLayout(layout)

        self.build_table()
        self.build_combobox()

    def accept_settings(self):
        self.settings.send_after_export = self.pb_send_after_export.isChecked()
        self.settings.current_dcc = self.cb_current_dcc.currentText()

    def on_close(self):
        pass

    def set_column_size(self):
        # total_width = 0
        # width = [0] * self.columns_count
        # for i in range(self.columns_count):
        #     w = self.dcc_table.columnWidth(i)
        #     total_width += w
        #     width[i] = w

        # ratios = [w / total_width for w in width]
        ratios = (0.5, 0.25, 0.25)

        availabed_width = self.dcc_table.size().width()
        for i in range(self.columns_count):
            self.dcc_table.setColumnWidth(i, availabed_width * ratios[i])

    def build_table(self):
        self.dcc_table.clear()

        self.dcc_table.setHorizontalScrollBarPolicy(Qt.Qt.ScrollBarAlwaysOff)
        self.dcc_table.setShowGrid(False)
        self.dcc_table.verticalHeader().setVisible(False)

        self.dcc_table.horizontalHeader().setSectionResizeMode(Qt.QHeaderView.ResizeMode.Fixed)

        self.dcc_table.setColumnCount(self.columns_count)
        self.dcc_table.setHorizontalHeaderLabels(self.columns)
        self.dcc_table.setRowCount(len(self.settings.dcc_settings))

        for i, (key, value) in enumerate(self.settings.dcc_settings.items()):
            item = Qt.QTableWidgetItem()
            item.setData(Qt.Qt.EditRole, value['port'])

            self.dcc_table.setItem(i, 0, Qt.QTableWidgetItem(key))
            self.dcc_table.setItem(i, 1, item)
            self.dcc_table.setItem(i, 2, Qt.QTableWidgetItem(value['format']))

        self.set_column_size()

    def resizeEvent(self, event):
        self.set_column_size()

    def on_show(self):
        self.set_column_size()

    def build_combobox(self):
        current_item = self.cb_current_dcc.currentText()
        if not current_item:
            current_item = self.settings.current_dcc

        self.cb_current_dcc.clear()

        items = list(self.settings.dcc_settings.keys())

        self.cb_current_dcc.addItems(items)

        try:
            self.cb_current_dcc.setCurrentIndex(items.index(current_item))
        except:
            pass


class SettingsDialog(Qt.QDialog):

    default_settings = {
        'core_collapsed': False,
        'dcc_collapsed': False,
        'geometry': None,
    }

    def __init__(self, main_ui):
        Qt.QDialog.__init__(self, main_ui, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle("Zlm Settings")

        self.main_ui = main_ui
        self.settings = zlm_settings.ZlmSettings.instance().get("settings_ui", self.default_settings)

        self.core_widget = CoreSettingWidget(self.settings['core_collapsed'])

        self.dcc_widget = DccSettingWidget(self.settings['dcc_collapsed'])

        pb_accept = Qt.QPushButton("Accept")
        pb_discard = Qt.QPushButton("Discard")

        pb_accept.clicked.connect(self.accept_settings)
        pb_discard.clicked.connect(self.discard_settings)

        main_widget = Qt.QWidget()
        widget_layout = Qt.QVBoxLayout()

        widget_layout.addWidget(self.core_widget)
        widget_layout.addWidget(self.dcc_widget)
        widget_layout.addStretch()

        main_widget.setLayout(widget_layout)

        scroll_area = Qt.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(main_widget)

        bottom_layout = Qt.QHBoxLayout()
        bottom_layout.setContentsMargins(10, 5, 10, 10)
        bottom_layout.addWidget(pb_accept)
        bottom_layout.addWidget(pb_discard)

        main_layout = Qt.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        if self.settings['geometry'] is not None:
            try:
                self.setGeometry(*self.settings['geometry'])
            except:
                pass

    def closeEvent(self, event):
        self.core_widget.on_close()
        self.dcc_widget.on_close()

        geo = self.geometry()
        self.settings['geometry'] = [geo.x(), geo.y(), geo.width(), geo.height()]
        self.settings['core_collapsed'] = self.core_widget.is_collapsed()

    def accept_settings(self):
        self.core_widget.accept_settings()
        self.dcc_widget.accept_settings()
        self.accept()

    def discard_settings(self):
        self.reject()

    def showEvent(self, event):
        self.dcc_widget.set_column_size()
