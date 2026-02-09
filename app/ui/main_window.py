"""
Claude 配置管理器主窗口
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QDialog, QFormLayout, QLineEdit, QFileDialog,
    QMessageBox, QLabel, QHeaderView, QAbstractItemView,
    QGroupBox, QSplitter, QCheckBox
)
from PySide6.QtCore import QSize

from .widgets.json_highlighter import JsonHighlighter


class ClaudeConfigGUI(QMainWindow):
    """Claude 配置管理器主窗口"""

    def __init__(self):
        super().__init__()
        self.config_path = Path.home() / ".claude.json"
        self.config_data = {}
        self.init_ui()
        self.load_config()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Claude Configuration Manager")
        self.setGeometry(100, 100, 1200, 750)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 5, 10, 10)

        # Config path label
        path_label = QLabel(f"配置文件: {self.config_path}")
        path_label.setStyleSheet("color: #666; font-size: 11px; padding: 2px 0;")
        main_layout.addWidget(path_label)

        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_general_settings_tab()
        self.create_mcp_servers_tab()
        self.create_projects_tab()
        self.create_user_info_tab()
        self.create_experimental_features_tab()
        self.create_raw_config_tab()

        # Status bar
        self.statusBar().showMessage("就绪")

    def create_general_settings_tab(self):
        """创建通用设置标签页"""
        from .tabs.general_settings_tab import GeneralSettingsTab
        tab = GeneralSettingsTab(self)
        self.general_settings_tab = tab
        self.tab_widget.addTab(tab, "通用设置")

    def create_mcp_servers_tab(self):
        """创建 MCP 服务器标签页"""
        from .tabs.mcp_servers_tab import MCPServersTab
        tab = MCPServersTab(self)
        self.mcp_servers_tab = tab
        self.tab_widget.addTab(tab, "MCP 服务器")

    def create_projects_tab(self):
        """创建项目列表标签页"""
        from .tabs.projects_tab import ProjectsTab
        tab = ProjectsTab(self)
        self.projects_tab = tab
        self.tab_widget.addTab(tab, "项目列表")

    def create_user_info_tab(self):
        """创建用户信息标签页"""
        from .tabs.user_info_tab import UserInfoTab
        tab = UserInfoTab(self)
        self.user_info_tab = tab
        self.tab_widget.addTab(tab, "用户信息")

    def create_experimental_features_tab(self):
        """创建实验性功能标签页"""
        from .tabs.experimental_features_tab import ExperimentalFeaturesTab
        tab = ExperimentalFeaturesTab(self)
        self.experimental_features_tab = tab
        self.tab_widget.addTab(tab, "实验性功能")

    def create_raw_config_tab(self):
        """创建原始 JSON 配置标签页"""
        from .tabs.raw_config_tab import RawConfigTab
        tab = RawConfigTab(self)
        self.raw_config_tab = tab
        self.tab_widget.addTab(tab, "完整配置 (JSON)")

    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                self.config_data = {}

            # 更新所有视图
            self.general_settings_tab.load_data(self.config_data)
            self.raw_config_tab.load_data(self.config_data)
            self.mcp_servers_tab.load_data(self.config_data)
            self.projects_tab.load_data(self.config_data)
            self.user_info_tab.load_data(self.config_data)
            self.experimental_features_tab.load_data(self.config_data)

            self.statusBar().showMessage(f"配置已加载: {self.config_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载配置文件失败:\n{str(e)}")
            self.statusBar().showMessage("加载失败")

    def save_config_to_file(self):
        """保存配置到文件"""
        try:
            # 备份原文件
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix('.json.bak')
                shutil.copy2(self.config_path, backup_path)

            # 写入新配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)

            self.statusBar().showMessage(f"配置已保存到: {self.config_path}")
        except Exception as e:
            raise Exception(f"保存到文件失败: {str(e)}")

    def get_config_data(self):
        """获取配置数据"""
        return self.config_data

    def set_config_data(self, data):
        """设置配置数据"""
        self.config_data = data

    def refresh_all_views(self):
        """刷新所有视图"""
        self.general_settings_tab.load_data(self.config_data)
        self.raw_config_tab.load_data(self.config_data)
        self.mcp_servers_tab.load_data(self.config_data)
        self.projects_tab.load_data(self.config_data)
        self.user_info_tab.load_data(self.config_data)
        self.experimental_features_tab.load_data(self.config_data)
