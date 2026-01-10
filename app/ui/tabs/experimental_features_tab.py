"""
实验性功能标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QAbstractItemView, QLabel, QGroupBox
)
from PySide6.QtCore import Qt


class ExperimentalFeaturesTab(QWidget):
    """实验性功能标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 信息标签
        info_label = QLabel("实验性功能开关 (这些是 A/B 测试和功能标志)")
        info_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addWidget(info_label)

        # Statsig Gates
        statsig_group = QGroupBox("Statsig 功能开关")
        statsig_layout = QVBoxLayout(statsig_group)

        self.statsig_table = QTableWidget()
        self.statsig_table.setColumnCount(2)
        self.statsig_table.setHorizontalHeaderLabels(["功能名称", "状态"])
        self.statsig_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.statsig_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.statsig_table.itemChanged.connect(self.on_statsig_item_changed)
        self.statsig_table.cellDoubleClicked.connect(self.toggle_statsig_feature)
        statsig_layout.addWidget(self.statsig_table)

        layout.addWidget(statsig_group)

        # GrowthBook Features
        growthbook_group = QGroupBox("GrowthBook 功能标志")
        growthbook_layout = QVBoxLayout(growthbook_group)

        self.growthbook_table = QTableWidget()
        self.growthbook_table.setColumnCount(2)
        self.growthbook_table.setHorizontalHeaderLabels(["功能名称", "值"])
        self.growthbook_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.growthbook_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.growthbook_table.itemChanged.connect(self.on_growthbook_item_changed)
        growthbook_layout.addWidget(self.growthbook_table)

        layout.addWidget(growthbook_group)

        # 保存按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存实验性设置")
        save_btn.clicked.connect(self.save_features)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def load_data(self, config_data):
        """加载数据"""
        # 阻止信号以防止加载时触发 itemChanged
        self.statsig_table.blockSignals(True)
        self.growthbook_table.blockSignals(True)

        # Statsig Gates
        statsig_gates = config_data.get("cachedStatsigGates", {})
        self.statsig_table.setRowCount(0)
        for name, value in statsig_gates.items():
            row = self.statsig_table.rowCount()
            self.statsig_table.insertRow(row)

            name_item = QTableWidgetItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.statsig_table.setItem(row, 0, name_item)

            value_item = QTableWidgetItem()
            value_item.setFlags(value_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            value_item.setCheckState(Qt.CheckState.Checked if value else Qt.CheckState.Unchecked)
            self.statsig_table.setItem(row, 1, value_item)

        # GrowthBook Features
        growthbook = config_data.get("cachedGrowthBookFeatures", {})
        self.growthbook_table.setRowCount(0)
        for name, value in growthbook.items():
            row = self.growthbook_table.rowCount()
            self.growthbook_table.insertRow(row)

            self.growthbook_table.setItem(row, 0, QTableWidgetItem(name))

            value_str = str(value) if value is not None else "null"
            self.growthbook_table.setItem(row, 1, QTableWidgetItem(value_str))

        # 解除阻塞
        self.statsig_table.blockSignals(False)
        self.growthbook_table.blockSignals(False)

    def on_statsig_item_changed(self, item):
        """Statsig 项目改变事件"""
        _ = item  # 值将在点击保存按钮时保存
        pass

    def on_growthbook_item_changed(self, item):
        """GrowthBook 项目改变事件"""
        _ = item  # 值将在点击保存按钮时保存
        pass

    def toggle_statsig_feature(self, row, col):
        """双击切换 Statsig 功能"""
        if col == 1:
            item = self.statsig_table.item(row, 1)
            current = item.checkState()
            item.setCheckState(Qt.CheckState.Unchecked if current == Qt.CheckState.Checked else Qt.CheckState.Checked)

    def save_features(self):
        """保存实验性功能设置"""
        try:
            config_data = self.parent_window.get_config_data()

            # 保存 Statsig Gates
            statsig_gates = {}
            for row in range(self.statsig_table.rowCount()):
                name_item = self.statsig_table.item(row, 0)
                value_item = self.statsig_table.item(row, 1)
                if name_item and value_item:
                    name = name_item.text()
                    value = value_item.checkState() == Qt.CheckState.Checked
                    statsig_gates[name] = value

            config_data["cachedStatsigGates"] = statsig_gates

            # 保存 GrowthBook Features
            growthbook = {}
            for row in range(self.growthbook_table.rowCount()):
                name_item = self.growthbook_table.item(row, 0)
                value_item = self.growthbook_table.item(row, 1)
                if name_item and value_item:
                    name = name_item.text()
                    value_str = value_item.text()

                    # 解析值
                    if value_str == "true":
                        value = True
                    elif value_str == "false":
                        value = False
                    elif value_str == "null":
                        value = None
                    elif value_str == "N/A":
                        value = "N/A"
                    elif value_str == "{}":
                        value = {}
                    else:
                        value = value_str

                    growthbook[name] = value

            config_data["cachedGrowthBookFeatures"] = growthbook

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            self.parent_window.raw_config_tab.load_data(config_data)

            QMessageBox.information(self, "成功", "实验性功能设置已保存!")
            self.parent_window.statusBar().showMessage("实验性功能已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}")
