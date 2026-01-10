"""
通用设置标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QCheckBox, QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt


class GeneralSettingsTab(QWidget):
    """通用设置标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 设置组
        settings_group = QGroupBox("通用设置")
        settings_layout = QFormLayout(settings_group)

        # 自动更新复选框
        self.auto_updates_checkbox = QCheckBox("启用自动更新")
        settings_layout.addRow(self.auto_updates_checkbox)

        # 安装方式(只读)
        self.install_method_label = QLabel()
        settings_layout.addRow("安装方式:", self.install_method_label)

        # 迁移状态组
        migration_group = QGroupBox("迁移状态")
        migration_layout = QFormLayout(migration_group)

        self.sonnet_migration_label = QLabel()
        self.opus_migration_label = QLabel()
        self.thinking_migration_label = QLabel()

        migration_layout.addRow("Sonnet 4.5:", self.sonnet_migration_label)
        migration_layout.addRow("Opus 4.5:", self.opus_migration_label)
        migration_layout.addRow("Thinking:", self.thinking_migration_label)

        # Marketplace 状态
        self.marketplace_attempted_label = QLabel()
        self.marketplace_installed_label = QLabel()
        migration_layout.addRow("市场插件尝试安装:", self.marketplace_attempted_label)
        migration_layout.addRow("市场插件已安装:", self.marketplace_installed_label)

        # 添加组到布局
        layout.addWidget(settings_group)
        layout.addWidget(migration_group)
        layout.addStretch()

        # 保存按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def load_data(self, config_data):
        """加载数据"""
        self.auto_updates_checkbox.setChecked(config_data.get("autoUpdates", False))
        self.install_method_label.setText(config_data.get("installMethod", "未知"))

        # 迁移状态
        sonnet = config_data.get("sonnet45MigrationComplete", False)
        opus = config_data.get("opus45MigrationComplete", False)
        thinking = config_data.get("thinkingMigrationComplete", False)

        self.sonnet_migration_label.setText("✓ 已完成" if sonnet else "✗ 未完成")
        self.sonnet_migration_label.setStyleSheet("color: green;" if sonnet else "color: red;")

        self.opus_migration_label.setText("✓ 已完成" if opus else "✗ 未完成")
        self.opus_migration_label.setStyleSheet("color: green;" if opus else "color: red;")

        self.thinking_migration_label.setText("✓ 已完成" if thinking else "✗ 未完成")
        self.thinking_migration_label.setStyleSheet("color: green;" if thinking else "color: red;")

        # Marketplace 状态
        attempted = config_data.get("officialMarketplaceAutoInstallAttempted", False)
        installed = config_data.get("officialMarketplaceAutoInstalled", False)

        self.marketplace_attempted_label.setText("是" if attempted else "否")
        self.marketplace_installed_label.setText("是" if installed else "否")

    def save_settings(self):
        """保存设置"""
        try:
            config_data = self.parent_window.get_config_data()
            config_data["autoUpdates"] = self.auto_updates_checkbox.isChecked()
            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            QMessageBox.information(self, "成功", "通用设置已保存!")
            self.parent_window.statusBar().showMessage("设置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败:\n{str(e)}")
