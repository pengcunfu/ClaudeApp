import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QDialog, QFormLayout, QLineEdit, QFileDialog,
    QMessageBox, QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
    QHeaderView, QAbstractItemView, QGroupBox, QSplitter,
    QCheckBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon


class ClaudeConfigGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_path = Path.home() / ".claude.json"
        self.config_data = {}
        self.init_ui()
        self.load_config()

    def init_ui(self):
        self.setWindowTitle("Claude Configuration Manager")
        self.setGeometry(100, 100, 1200, 750)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Header
        header_label = QLabel("Claude Configuration Manager")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)

        # Config path label
        path_label = QLabel(f"配置文件: {self.config_path}")
        path_label.setStyleSheet("color: #666; font-size: 11px;")
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
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Settings group
        settings_group = QGroupBox("通用设置")
        settings_layout = QFormLayout(settings_group)

        # Auto updates checkbox
        self.auto_updates_checkbox = QCheckBox("启用自动更新")
        settings_layout.addRow(self.auto_updates_checkbox)

        # Install method (read-only)
        self.install_method_label = QLabel()
        settings_layout.addRow("安装方式:", self.install_method_label)

        # Migration status group
        migration_group = QGroupBox("迁移状态")
        migration_layout = QFormLayout(migration_group)

        self.sonnet_migration_label = QLabel()
        self.opus_migration_label = QLabel()
        self.thinking_migration_label = QLabel()

        migration_layout.addRow("Sonnet 4.5:", self.sonnet_migration_label)
        migration_layout.addRow("Opus 4.5:", self.opus_migration_label)
        migration_layout.addRow("Thinking:", self.thinking_migration_label)

        # Marketplace status
        self.marketplace_attempted_label = QLabel()
        self.marketplace_installed_label = QLabel()
        migration_layout.addRow("市场插件尝试安装:", self.marketplace_attempted_label)
        migration_layout.addRow("市场插件已安装:", self.marketplace_installed_label)

        # Add groups to layout
        layout.addWidget(settings_group)
        layout.addWidget(migration_group)
        layout.addStretch()

        # Save button
        button_layout = QHBoxLayout()
        self.save_general_btn = QPushButton("保存设置")
        self.save_general_btn.clicked.connect(self.save_general_settings)
        button_layout.addStretch()
        button_layout.addWidget(self.save_general_btn)
        layout.addLayout(button_layout)

        self.tab_widget.addTab(tab, "通用设置")

    def create_mcp_servers_tab(self):
        """Create MCP servers management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_mcp_btn = QPushButton("添加服务器")
        self.edit_mcp_btn = QPushButton("编辑服务器")
        self.delete_mcp_btn = QPushButton("删除服务器")

        self.add_mcp_btn.clicked.connect(self.add_mcp_server)
        self.edit_mcp_btn.clicked.connect(self.edit_mcp_server)
        self.delete_mcp_btn.clicked.connect(self.delete_mcp_server)

        button_layout.addWidget(self.add_mcp_btn)
        button_layout.addWidget(self.edit_mcp_btn)
        button_layout.addWidget(self.delete_mcp_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Table
        self.mcp_table = QTableWidget()
        self.mcp_table.setColumnCount(4)
        self.mcp_table.setHorizontalHeaderLabels(["服务器名称", "命令", "参数", "环境变量"])
        self.mcp_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.mcp_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.mcp_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.mcp_table.itemDoubleClicked.connect(self.edit_mcp_server)
        layout.addWidget(self.mcp_table)

        self.tab_widget.addTab(tab, "MCP 服务器")

    def create_projects_tab(self):
        """Create projects management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Info label
        info_label = QLabel("GitHub 仓库路径配置:")
        layout.addWidget(info_label)

        # Splitter for repo list and paths
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Repo list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Repo list buttons
        repo_btn_layout = QHBoxLayout()
        add_repo_btn = QPushButton("添加仓库")
        delete_repo_btn = QPushButton("删除仓库")
        add_repo_btn.clicked.connect(self.add_repo)
        delete_repo_btn.clicked.connect(self.delete_repo)
        repo_btn_layout.addWidget(add_repo_btn)
        repo_btn_layout.addWidget(delete_repo_btn)
        repo_btn_layout.addStretch()
        left_layout.addLayout(repo_btn_layout)

        self.repo_table = QTableWidget()
        self.repo_table.setColumnCount(2)
        self.repo_table.setHorizontalHeaderLabels(["仓库", "路径数量"])
        self.repo_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.repo_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.repo_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.repo_table.itemSelectionChanged.connect(self.on_repo_selected)
        left_layout.addWidget(self.repo_table)

        splitter.addWidget(left_widget)

        # Right side: Path details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Path buttons
        path_btn_layout = QHBoxLayout()
        add_path_btn = QPushButton("添加路径")
        remove_path_btn = QPushButton("删除路径")
        add_path_btn.clicked.connect(self.add_path)
        remove_path_btn.clicked.connect(self.remove_path)
        path_btn_layout.addWidget(add_path_btn)
        path_btn_layout.addWidget(remove_path_btn)
        path_btn_layout.addStretch()
        right_layout.addLayout(path_btn_layout)

        right_label = QLabel("本地路径:")
        right_layout.addWidget(right_label)

        self.path_table = QTableWidget()
        self.path_table.setColumnCount(1)
        self.path_table.setHorizontalHeaderLabels(["路径"])
        self.path_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.path_table)

        splitter.addWidget(right_widget)

        layout.addWidget(splitter)

        self.tab_widget.addTab(tab, "项目列表")

    def create_user_info_tab(self):
        """Create user information tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # User info group
        user_group = QGroupBox("用户信息")
        user_layout = QFormLayout(user_group)

        self.user_id_label = QLabel()
        self.user_id_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.user_id_label.setWordWrap(True)
        user_layout.addRow("用户ID:", self.user_id_label)

        self.first_start_label = QLabel()
        user_layout.addRow("首次使用时间:", self.first_start_label)

        # Calculate usage time
        self.usage_time_label = QLabel()
        user_layout.addRow("使用时长:", self.usage_time_label)

        layout.addWidget(user_group)

        # Export/Import group
        backup_group = QGroupBox("配置备份与恢复")
        backup_layout = QVBoxLayout(backup_group)

        export_btn = QPushButton("导出配置")
        import_btn = QPushButton("导入配置")
        reset_btn = QPushButton("重置为默认")

        export_btn.clicked.connect(self.export_config)
        import_btn.clicked.connect(self.import_config)
        reset_btn.clicked.connect(self.reset_config)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(import_btn)
        btn_layout.addWidget(reset_btn)
        backup_layout.addLayout(btn_layout)

        # Backup info
        backup_info = QLabel("提示: 保存配置时会自动创建 .bak 备份文件")
        backup_info.setStyleSheet("color: #666; font-size: 10px;")
        backup_layout.addWidget(backup_info)

        layout.addWidget(backup_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "用户信息")

    def create_experimental_features_tab(self):
        """Create experimental features tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Info label
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

        # Save button
        button_layout = QHBoxLayout()
        self.save_experimental_btn = QPushButton("保存实验性设置")
        self.save_experimental_btn.clicked.connect(self.save_experimental_features)
        button_layout.addStretch()
        button_layout.addWidget(self.save_experimental_btn)
        layout.addLayout(button_layout)

        self.tab_widget.addTab(tab, "实验性功能")

    def create_raw_config_tab(self):
        """Create raw JSON config viewer/editor tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Buttons
        button_layout = QHBoxLayout()
        self.reload_btn = QPushButton("重新加载")
        self.save_btn = QPushButton("保存配置")
        self.format_btn = QPushButton("格式化JSON")

        self.reload_btn.clicked.connect(self.load_config)
        self.save_btn.clicked.connect(self.save_raw_config)
        self.format_btn.clicked.connect(self.format_json)

        button_layout.addWidget(self.reload_btn)
        button_layout.addWidget(self.format_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Text editor
        self.raw_config_text = QTextEdit()
        self.raw_config_text.setFont(QFont("Consolas", 10))
        self.raw_config_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.raw_config_text)

        self.tab_widget.addTab(tab, "完整配置 (JSON)")

    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                self.config_data = {}

            # Update all views
            self.update_general_settings()
            self.update_raw_config_view()
            self.update_mcp_table()
            self.update_projects_table()
            self.update_user_info()
            self.update_experimental_features()

            self.statusBar().showMessage(f"配置已加载: {self.config_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载配置文件失败:\n{str(e)}")
            self.statusBar().showMessage("加载失败")

    def update_general_settings(self):
        """Update general settings view"""
        self.auto_updates_checkbox.setChecked(self.config_data.get("autoUpdates", False))
        self.install_method_label.setText(self.config_data.get("installMethod", "未知"))

        # Migration status
        sonnet = self.config_data.get("sonnet45MigrationComplete", False)
        opus = self.config_data.get("opus45MigrationComplete", False)
        thinking = self.config_data.get("thinkingMigrationComplete", False)

        self.sonnet_migration_label.setText("✓ 已完成" if sonnet else "✗ 未完成")
        self.sonnet_migration_label.setStyleSheet("color: green;" if sonnet else "color: red;")

        self.opus_migration_label.setText("✓ 已完成" if opus else "✗ 未完成")
        self.opus_migration_label.setStyleSheet("color: green;" if opus else "color: red;")

        self.thinking_migration_label.setText("✓ 已完成" if thinking else "✗ 未完成")
        self.thinking_migration_label.setStyleSheet("color: green;" if thinking else "color: red;")

        # Marketplace status
        attempted = self.config_data.get("officialMarketplaceAutoInstallAttempted", False)
        installed = self.config_data.get("officialMarketplaceAutoInstalled", False)

        self.marketplace_attempted_label.setText("是" if attempted else "否")
        self.marketplace_installed_label.setText("是" if installed else "否")

    def update_raw_config_view(self):
        """Update raw JSON editor"""
        json_str = json.dumps(self.config_data, indent=2, ensure_ascii=False)
        self.raw_config_text.setPlainText(json_str)

    def update_mcp_table(self):
        """Update MCP servers table"""
        mcp_servers = self.config_data.get("mcpServers", {})

        self.mcp_table.setRowCount(0)
        for name, config in mcp_servers.items():
            row = self.mcp_table.rowCount()
            self.mcp_table.insertRow(row)

            self.mcp_table.setItem(row, 0, QTableWidgetItem(name))
            self.mcp_table.setItem(row, 1, QTableWidgetItem(config.get("command", "")))
            self.mcp_table.setItem(row, 2, QTableWidgetItem(str(config.get("args", []))))

            env = config.get("env", {})
            env_str = "; ".join([f"{k}={v}" for k, v in env.items()])
            self.mcp_table.setItem(row, 3, QTableWidgetItem(env_str))

    def update_projects_table(self):
        """Update projects table"""
        github_repos = self.config_data.get("githubRepoPaths", {})

        self.repo_table.setRowCount(0)
        for repo_name, paths in github_repos.items():
            row = self.repo_table.rowCount()
            self.repo_table.insertRow(row)

            self.repo_table.setItem(row, 0, QTableWidgetItem(repo_name))
            self.repo_table.setItem(row, 1, QTableWidgetItem(str(len(paths))))

        # Clear path table
        self.path_table.setRowCount(0)

    def on_repo_selected(self):
        """Handle repo selection change"""
        selected_items = self.repo_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        repo_name = self.repo_table.item(row, 0).text()

        github_repos = self.config_data.get("githubRepoPaths", {})
        paths = github_repos.get(repo_name, [])

        self.path_table.setRowCount(0)
        for path in paths:
            path_row = self.path_table.rowCount()
            self.path_table.insertRow(path_row)
            self.path_table.setItem(path_row, 0, QTableWidgetItem(path))

    def update_user_info(self):
        """Update user information view"""
        user_id = self.config_data.get("userID", "未知")
        self.user_id_label.setText(user_id)

        first_start = self.config_data.get("firstStartTime", "")
        if first_start:
            try:
                # Parse ISO 8601 format
                start_time = datetime.fromisoformat(first_start.replace('Z', '+00:00'))
                # Convert to local timezone
                local_time = start_time.astimezone()
                formatted = local_time.strftime("%Y-%m-%d %H:%M:%S")
                self.first_start_label.setText(formatted)

                # Calculate usage duration
                now = datetime.now(local_time.tzinfo)
                duration = now - local_time
                days = duration.days
                hours = duration.seconds // 3600
                self.usage_time_label.setText(f"{days} 天 {hours} 小时")
            except:
                self.first_start_label.setText(first_start)
                self.usage_time_label.setText("未知")
        else:
            self.first_start_label.setText("未知")
            self.usage_time_label.setText("未知")

    def update_experimental_features(self):
        """Update experimental features tables"""
        # Block signals to prevent triggering itemChanged during load
        self.statsig_table.blockSignals(True)
        self.growthbook_table.blockSignals(True)

        # Statsig Gates
        statsig_gates = self.config_data.get("cachedStatsigGates", {})
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
        growthbook = self.config_data.get("cachedGrowthBookFeatures", {})
        self.growthbook_table.setRowCount(0)
        for name, value in growthbook.items():
            row = self.growthbook_table.rowCount()
            self.growthbook_table.insertRow(row)

            self.growthbook_table.setItem(row, 0, QTableWidgetItem(name))

            value_str = str(value) if value is not None else "null"
            self.growthbook_table.setItem(row, 1, QTableWidgetItem(value_str))

        # Unblock signals
        self.statsig_table.blockSignals(False)
        self.growthbook_table.blockSignals(False)

    def on_statsig_item_changed(self, item):
        """Handle Statsig item change"""
        _ = item  # Value will be saved when Save button is clicked
        pass

    def on_growthbook_item_changed(self, item):
        """Handle GrowthBook item change"""
        _ = item  # Value will be saved when Save button is clicked
        pass

    def toggle_statsig_feature(self, row, col):
        """Toggle Statsig feature on double-click"""
        if col == 1:
            item = self.statsig_table.item(row, 1)
            current = item.checkState()
            item.setCheckState(Qt.CheckState.Unchecked if current == Qt.CheckState.Checked else Qt.CheckState.Checked)

    def save_general_settings(self):
        """Save general settings"""
        try:
            self.config_data["autoUpdates"] = self.auto_updates_checkbox.isChecked()
            self.save_config_to_file()
            QMessageBox.information(self, "成功", "通用设置已保存!")
            self.statusBar().showMessage("设置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败:\n{str(e)}")

    def save_experimental_features(self):
        """Save experimental features"""
        try:
            # Save Statsig Gates
            statsig_gates = {}
            for row in range(self.statsig_table.rowCount()):
                name_item = self.statsig_table.item(row, 0)
                value_item = self.statsig_table.item(row, 1)
                if name_item and value_item:
                    name = name_item.text()
                    value = value_item.checkState() == Qt.CheckState.Checked
                    statsig_gates[name] = value

            self.config_data["cachedStatsigGates"] = statsig_gates

            # Save GrowthBook Features
            growthbook = {}
            for row in range(self.growthbook_table.rowCount()):
                name_item = self.growthbook_table.item(row, 0)
                value_item = self.growthbook_table.item(row, 1)
                if name_item and value_item:
                    name = name_item.text()
                    value_str = value_item.text()

                    # Parse value
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

            self.config_data["cachedGrowthBookFeatures"] = growthbook

            self.save_config_to_file()
            self.update_raw_config_view()

            QMessageBox.information(self, "成功", "实验性功能设置已保存!")
            self.statusBar().showMessage("实验性功能已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}")

    def add_repo(self):
        """Add new GitHub repo"""
        dialog = RepoDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            repo_name = dialog.get_repo_name()

            if "githubRepoPaths" not in self.config_data:
                self.config_data["githubRepoPaths"] = {}

            self.config_data["githubRepoPaths"][repo_name] = []

            self.save_config_to_file()
            self.update_projects_table()
            self.update_raw_config_view()

            QMessageBox.information(self, "成功", f"仓库 '{repo_name}' 已添加!")

    def delete_repo(self):
        """Delete selected repo"""
        selected_items = self.repo_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个仓库")
            return

        row = selected_items[0].row()
        repo_name = self.repo_table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除仓库 '{repo_name}' 吗?\n这将删除该仓库的所有路径配置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            github_repos = self.config_data.get("githubRepoPaths", {})
            if repo_name in github_repos:
                del github_repos[repo_name]

                self.save_config_to_file()
                self.update_projects_table()
                self.update_raw_config_view()

                QMessageBox.information(self, "成功", f"仓库 '{repo_name}' 已删除!")

    def add_path(self):
        """Add path to selected repo"""
        selected_items = self.repo_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个仓库")
            return

        row = selected_items[0].row()
        repo_name = self.repo_table.item(row, 0).text()

        # Browse for folder
        folder_path = QFileDialog.getExistingDirectory(self, "选择项目文件夹")
        if folder_path:
            github_repos = self.config_data.get("githubRepoPaths", {})
            if repo_name in github_repos:
                paths = github_repos[repo_name]
                if folder_path not in paths:
                    paths.append(folder_path)

                    self.save_config_to_file()
                    self.update_projects_table()
                    self.on_repo_selected()
                    self.update_raw_config_view()

                    QMessageBox.information(self, "成功", f"路径已添加到 '{repo_name}'!")
                else:
                    QMessageBox.warning(self, "警告", "该路径已存在")

    def remove_path(self):
        """Remove selected path"""
        selected_repo_items = self.repo_table.selectedItems()
        selected_path_items = self.path_table.selectedItems()

        if not selected_repo_items or not selected_path_items:
            QMessageBox.warning(self, "警告", "请先选择仓库和路径")
            return

        repo_row = selected_repo_items[0].row()
        repo_name = self.repo_table.item(repo_row, 0).text()

        path_row = selected_path_items[0].row()
        path = self.path_table.item(path_row, 0).text()

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除路径 '{path}' 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            github_repos = self.config_data.get("githubRepoPaths", {})
            if repo_name in github_repos:
                paths = github_repos[repo_name]
                if path in paths:
                    paths.remove(path)

                    self.save_config_to_file()
                    self.update_projects_table()
                    self.on_repo_selected()
                    self.update_raw_config_view()

                    QMessageBox.information(self, "成功", "路径已删除!")

    def export_config(self):
        """Export configuration to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出配置",
            str(Path.home() / "claude_config_backup.json"),
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config_data, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "成功", f"配置已导出到:\n{file_path}")
                self.statusBar().showMessage(f"配置已导出: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")

    def import_config(self):
        """Import configuration from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入配置",
            str(Path.home()),
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )

        if file_path:
            reply = QMessageBox.question(
                self, "确认导入",
                "导入配置将覆盖当前配置,确定要继续吗?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        imported_data = json.load(f)

                    # Backup current config
                    if self.config_path.exists():
                        backup_path = self.config_path.with_suffix('.json.bak')
                        shutil.copy2(self.config_path, backup_path)

                    # Update config
                    self.config_data = imported_data
                    self.save_config_to_file()

                    # Refresh all views
                    self.load_config()

                    QMessageBox.information(self, "成功", "配置已导入!")
                    self.statusBar().showMessage(f"配置已导入: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"导入失败:\n{str(e)}")

    def reset_config(self):
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self, "确认重置",
            "重置配置将删除所有自定义设置!\n此操作不可撤销。\n\n确定要继续吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Create backup
                if self.config_path.exists():
                    backup_path = self.config_path.with_suffix(f'.json.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                    shutil.copy2(self.config_path, backup_path)

                # Reset to minimal config
                self.config_data = {
                    "installMethod": "native",
                    "autoUpdates": False,
                    "mcpServers": {},
                    "githubRepoPaths": {}
                }

                self.save_config_to_file()
                self.load_config()

                QMessageBox.information(self, "成功", "配置已重置为默认值!")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"重置失败:\n{str(e)}")

    def save_raw_config(self):
        """Save raw JSON configuration"""
        try:
            json_text = self.raw_config_text.toPlainText()
            self.config_data = json.loads(json_text)

            self.save_config_to_file()

            # Update all views
            self.update_general_settings()
            self.update_mcp_table()
            self.update_projects_table()
            self.update_user_info()
            self.update_experimental_features()

            QMessageBox.information(self, "成功", "配置已保存!")
            self.statusBar().showMessage("配置已保存")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "错误", f"JSON 格式错误:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")

    def format_json(self):
        """Format JSON in the text editor"""
        try:
            json_text = self.raw_config_text.toPlainText()
            data = json.loads(json_text)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            self.raw_config_text.setPlainText(formatted)
            self.statusBar().showMessage("JSON已格式化")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "错误", f"JSON 格式错误:\n{str(e)}")

    def add_mcp_server(self):
        """Add new MCP server"""
        dialog = MCPServerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            server_data = dialog.get_server_data()

            if "mcpServers" not in self.config_data:
                self.config_data["mcpServers"] = {}

            self.config_data["mcpServers"][server_data["name"]] = {
                "command": server_data["command"],
                "args": server_data["args"]
            }

            if server_data["env_vars"]:
                self.config_data["mcpServers"][server_data["name"]]["env"] = server_data["env_vars"]

            self.save_config_to_file()
            self.update_mcp_table()
            self.update_raw_config_view()

            QMessageBox.information(self, "成功", f"MCP服务器 '{server_data['name']}' 已添加!")

    def edit_mcp_server(self):
        """Edit selected MCP server"""
        selected_items = self.mcp_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个服务器")
            return

        row = selected_items[0].row()
        server_name = self.mcp_table.item(row, 0).text()

        mcp_servers = self.config_data.get("mcpServers", {})
        if server_name not in mcp_servers:
            return

        server_config = mcp_servers[server_name]

        dialog = MCPServerDialog(self, server_name, server_config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            server_data = dialog.get_server_data()

            # Remove old entry if name changed
            if server_data["name"] != server_name:
                del mcp_servers[server_name]

            mcp_servers[server_data["name"]] = {
                "command": server_data["command"],
                "args": server_data["args"]
            }

            if server_data["env_vars"]:
                mcp_servers[server_data["name"]]["env"] = server_data["env_vars"]

            self.save_config_to_file()
            self.update_mcp_table()
            self.update_raw_config_view()

            QMessageBox.information(self, "成功", f"MCP服务器 '{server_data['name']}' 已更新!")

    def delete_mcp_server(self):
        """Delete selected MCP server"""
        selected_items = self.mcp_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个服务器")
            return

        row = selected_items[0].row()
        server_name = self.mcp_table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除MCP服务器 '{server_name}' 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            mcp_servers = self.config_data.get("mcpServers", {})
            if server_name in mcp_servers:
                del mcp_servers[server_name]

                self.save_config_to_file()
                self.update_mcp_table()
                self.update_raw_config_view()

                QMessageBox.information(self, "成功", f"MCP服务器 '{server_name}' 已删除!")

    def save_config_to_file(self):
        """Save configuration to file"""
        try:
            # Backup original file
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix('.json.bak')
                shutil.copy2(self.config_path, backup_path)

            # Write new config
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)

            self.statusBar().showMessage(f"配置已保存到: {self.config_path}")
        except Exception as e:
            raise Exception(f"保存到文件失败: {str(e)}")


class MCPServerDialog(QDialog):
    """Dialog for adding/editing MCP server configuration"""

    def __init__(self, parent, name="", config=None):
        super().__init__(parent)
        self.name = name
        self.config = config or {}
        self.env_vars = {}
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("MCP 服务器配置")
        self.setMinimumWidth(600)

        layout = QFormLayout(self)

        # Server name
        self.name_edit = QLineEdit()
        layout.addRow("服务器名称:", self.name_edit)

        # Command
        self.command_edit = QLineEdit()
        self.command_btn = QPushButton("浏览...")
        self.command_btn.clicked.connect(self.browse_command)
        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(self.command_edit)
        cmd_layout.addWidget(self.command_btn)
        layout.addRow("命令:", cmd_layout)

        # Arguments
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText('用空格分隔参数,例如: --host localhost --port 3306')
        layout.addRow("参数:", self.args_edit)

        # Environment variables
        env_group = QGroupBox("环境变量 (可选)")
        env_layout = QVBoxLayout(env_group)

        self.env_table = QTableWidget()
        self.env_table.setColumnCount(2)
        self.env_table.setHorizontalHeaderLabels(["变量名", "值"])
        self.env_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.env_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        env_layout.addWidget(self.env_table)

        env_btn_layout = QHBoxLayout()
        add_env_btn = QPushButton("添加变量")
        remove_env_btn = QPushButton("删除变量")
        add_env_btn.clicked.connect(self.add_env_var)
        remove_env_btn.clicked.connect(self.remove_env_var)
        env_btn_layout.addWidget(add_env_btn)
        env_btn_layout.addWidget(remove_env_btn)
        env_btn_layout.addStretch()
        env_layout.addLayout(env_btn_layout)

        layout.addRow(env_group)

        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def load_data(self):
        """Load existing data if editing"""
        if self.config:
            self.name_edit.setText(self.name)
            self.command_edit.setText(self.config.get("command", ""))

            args = self.config.get("args", [])
            self.args_edit.setText(" ".join(args))

            env = self.config.get("env", {})
            for key, value in env.items():
                self.add_env_row(key, value)

    def browse_command(self):
        """Browse for executable file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择可执行文件",
            str(Path.home()),
            "可执行文件 (*.exe *.bat *.cmd);;所有文件 (*.*)"
        )
        if file_path:
            self.command_edit.setText(file_path)

    def add_env_var(self):
        """Add new environment variable row"""
        self.add_env_row("", "")
        # Select the new row
        row = self.env_table.rowCount() - 1
        self.env_table.selectRow(row)

    def add_env_row(self, key, value):
        """Add a row to the environment variables table"""
        row = self.env_table.rowCount()
        self.env_table.insertRow(row)
        self.env_table.setItem(row, 0, QTableWidgetItem(key))
        self.env_table.setItem(row, 1, QTableWidgetItem(value))

    def remove_env_var(self):
        """Remove selected environment variable"""
        selected_items = self.env_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.env_table.removeRow(row)

    def get_server_data(self):
        """Get server data from form"""
        name = self.name_edit.text().strip()
        if not name:
            raise ValueError("服务器名称不能为空")

        command = self.command_edit.text().strip()
        if not command:
            raise ValueError("命令不能为空")

        # Parse arguments
        args_text = self.args_edit.text().strip()
        args = []
        if args_text:
            # Simple split by spaces (could be improved)
            import shlex
            try:
                args = shlex.split(args_text)
            except:
                args = args_text.split()

        # Get environment variables
        env_vars = {}
        for row in range(self.env_table.rowCount()):
            key_item = self.env_table.item(row, 0)
            value_item = self.env_table.item(row, 1)

            if key_item and value_item:
                key = key_item.text().strip()
                value = value_item.text().strip()
                if key:
                    env_vars[key] = value

        return {
            "name": name,
            "command": command,
            "args": args,
            "env_vars": env_vars
        }


class RepoDialog(QDialog):
    """Dialog for adding GitHub repo"""

    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("添加 GitHub 仓库")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        self.repo_edit = QLineEdit()
        self.repo_edit.setPlaceholderText("例如: username/repo-name")
        layout.addRow("仓库名称:", self.repo_edit)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def validate_and_accept(self):
        repo_name = self.repo_edit.text().strip()
        if not repo_name:
            QMessageBox.warning(self, "警告", "仓库名称不能为空")
            return
        if "/" not in repo_name:
            QMessageBox.warning(self, "警告", "仓库名称格式应为: username/repo-name")
            return
        self.accept()

    def get_repo_name(self):
        return self.repo_edit.text().strip()


def main():
    import sys

    # PySide6 自动处理 High DPI,无需手动设置
    app = QApplication(sys.argv)

    # Set Windows Vista style
    app.setStyle("WindowsVista")

    window = ClaudeConfigGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
