import json
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QDialog, QFormLayout, QLineEdit, QFileDialog,
    QMessageBox, QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
    QHeaderView, QAbstractItemView, QGroupBox, QSplitter
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
        self.setGeometry(100, 100, 1200, 700)

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
        self.create_raw_config_tab()
        self.create_mcp_servers_tab()
        self.create_projects_tab()

        # Status bar
        self.statusBar().showMessage("Ready")

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

        right_label = QLabel("路径详情:")
        right_layout.addWidget(right_label)

        self.path_table = QTableWidget()
        self.path_table.setColumnCount(1)
        self.path_table.setHorizontalHeaderLabels(["本地路径"])
        self.path_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.path_table)

        splitter.addWidget(right_widget)

        layout.addWidget(splitter)

        self.tab_widget.addTab(tab, "项目列表")

    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                self.config_data = {}

            # Update all views
            self.update_raw_config_view()
            self.update_mcp_table()
            self.update_projects_table()

            self.statusBar().showMessage(f"配置已加载: {self.config_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载配置文件失败:\n{str(e)}")
            self.statusBar().showMessage("加载失败")

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

    def save_raw_config(self):
        """Save raw JSON configuration"""
        try:
            json_text = self.raw_config_text.toPlainText()
            self.config_data = json.loads(json_text)

            self.save_config_to_file()
            self.update_mcp_table()
            self.update_projects_table()

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
                import shutil
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
