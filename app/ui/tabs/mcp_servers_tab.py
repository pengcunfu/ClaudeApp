"""
MCP 服务器标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt


class MCPServersTab(QWidget):
    """MCP 服务器标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 按钮栏
        button_layout = QHBoxLayout()
        add_btn = QPushButton("添加服务器")
        edit_btn = QPushButton("编辑服务器")
        delete_btn = QPushButton("删除服务器")

        add_btn.clicked.connect(self.add_server)
        edit_btn.clicked.connect(self.edit_server)
        delete_btn.clicked.connect(self.delete_server)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["服务器名称", "命令", "参数", "环境变量"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.edit_server)
        layout.addWidget(self.table)

    def load_data(self, config_data):
        """加载数据"""
        mcp_servers = config_data.get("mcpServers", {})

        self.table.setRowCount(0)
        for name, config in mcp_servers.items():
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(config.get("command", "")))
            self.table.setItem(row, 2, QTableWidgetItem(str(config.get("args", []))))

            env = config.get("env", {})
            env_str = "; ".join([f"{k}={v}" for k, v in env.items()])
            self.table.setItem(row, 3, QTableWidgetItem(env_str))

    def add_server(self):
        """添加服务器"""
        from ..dialogs.mcp_server_dialog import MCPServerDialog
        dialog = MCPServerDialog(self)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            server_data = dialog.get_server_data()

            config_data = self.parent_window.get_config_data()
            if "mcpServers" not in config_data:
                config_data["mcpServers"] = {}

            config_data["mcpServers"][server_data["name"]] = {
                "command": server_data["command"],
                "args": server_data["args"]
            }

            if server_data["env_vars"]:
                config_data["mcpServers"][server_data["name"]]["env"] = server_data["env_vars"]

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            self.load_data(config_data)
            self.parent_window.raw_config_tab.load_data(config_data)

            QMessageBox.information(self, "成功", f"MCP服务器 '{server_data['name']}' 已添加!")

    def edit_server(self):
        """编辑服务器"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个服务器")
            return

        row = selected_items[0].row()
        server_name = self.table.item(row, 0).text()

        config_data = self.parent_window.get_config_data()
        mcp_servers = config_data.get("mcpServers", {})
        if server_name not in mcp_servers:
            return

        server_config = mcp_servers[server_name]

        from ..dialogs.mcp_server_dialog import MCPServerDialog
        dialog = MCPServerDialog(self, server_name, server_config)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            server_data = dialog.get_server_data()

            # 如果名称改变,删除旧条目
            if server_data["name"] != server_name:
                del mcp_servers[server_name]

            mcp_servers[server_data["name"]] = {
                "command": server_data["command"],
                "args": server_data["args"]
            }

            if server_data["env_vars"]:
                mcp_servers[server_data["name"]]["env"] = server_data["env_vars"]

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            self.load_data(config_data)
            self.parent_window.raw_config_tab.load_data(config_data)

            QMessageBox.information(self, "成功", f"MCP服务器 '{server_data['name']}' 已更新!")

    def delete_server(self):
        """删除服务器"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个服务器")
            return

        row = selected_items[0].row()
        server_name = self.table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除MCP服务器 '{server_name}' 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            config_data = self.parent_window.get_config_data()
            mcp_servers = config_data.get("mcpServers", {})
            if server_name in mcp_servers:
                del mcp_servers[server_name]

                self.parent_window.set_config_data(config_data)
                self.parent_window.save_config_to_file()
                self.load_data(config_data)
                self.parent_window.raw_config_tab.load_data(config_data)

                QMessageBox.information(self, "成功", f"MCP服务器 '{server_name}' 已删除!")
