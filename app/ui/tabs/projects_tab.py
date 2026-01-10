"""
项目列表标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QAbstractItemView,
    QSplitter, QLabel, QFileDialog
)
from PySide6.QtCore import Qt


class ProjectsTab(QWidget):
    """项目列表标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 信息标签
        info_label = QLabel("GitHub 仓库路径配置:")
        layout.addWidget(info_label)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧: 仓库列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 仓库按钮
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

        # 右侧: 路径详情
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 路径按钮
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

    def load_data(self, config_data):
        """加载数据"""
        github_repos = config_data.get("githubRepoPaths", {})

        self.repo_table.setRowCount(0)
        for repo_name, paths in github_repos.items():
            row = self.repo_table.rowCount()
            self.repo_table.insertRow(row)

            self.repo_table.setItem(row, 0, QTableWidgetItem(repo_name))
            self.repo_table.setItem(row, 1, QTableWidgetItem(str(len(paths))))

        # 清空路径表
        self.path_table.setRowCount(0)

    def on_repo_selected(self):
        """仓库选择改变事件"""
        selected_items = self.repo_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        repo_name = self.repo_table.item(row, 0).text()

        config_data = self.parent_window.get_config_data()
        github_repos = config_data.get("githubRepoPaths", {})
        paths = github_repos.get(repo_name, [])

        self.path_table.setRowCount(0)
        for path in paths:
            path_row = self.path_table.rowCount()
            self.path_table.insertRow(path_row)
            self.path_table.setItem(path_row, 0, QTableWidgetItem(path))

    def add_repo(self):
        """添加仓库"""
        from ..dialogs.repo_dialog import RepoDialog
        dialog = RepoDialog(self)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            repo_name = dialog.get_repo_name()

            config_data = self.parent_window.get_config_data()
            if "githubRepoPaths" not in config_data:
                config_data["githubRepoPaths"] = {}

            config_data["githubRepoPaths"][repo_name] = []

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            self.load_data(config_data)
            self.parent_window.raw_config_tab.load_data(config_data)

            QMessageBox.information(self, "成功", f"仓库 '{repo_name}' 已添加!")

    def delete_repo(self):
        """删除仓库"""
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
            config_data = self.parent_window.get_config_data()
            github_repos = config_data.get("githubRepoPaths", {})
            if repo_name in github_repos:
                del github_repos[repo_name]

                self.parent_window.set_config_data(config_data)
                self.parent_window.save_config_to_file()
                self.load_data(config_data)
                self.parent_window.raw_config_tab.load_data(config_data)

                QMessageBox.information(self, "成功", f"仓库 '{repo_name}' 已删除!")

    def add_path(self):
        """添加路径"""
        selected_items = self.repo_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个仓库")
            return

        row = selected_items[0].row()
        repo_name = self.repo_table.item(row, 0).text()

        # 浏览文件夹
        folder_path = QFileDialog.getExistingDirectory(self, "选择项目文件夹")
        if folder_path:
            config_data = self.parent_window.get_config_data()
            github_repos = config_data.get("githubRepoPaths", {})
            if repo_name in github_repos:
                paths = github_repos[repo_name]
                if folder_path not in paths:
                    paths.append(folder_path)

                    self.parent_window.set_config_data(config_data)
                    self.parent_window.save_config_to_file()
                    self.load_data(config_data)
                    self.on_repo_selected()
                    self.parent_window.raw_config_tab.load_data(config_data)

                    QMessageBox.information(self, "成功", f"路径已添加到 '{repo_name}'!")
                else:
                    QMessageBox.warning(self, "警告", "该路径已存在")

    def remove_path(self):
        """删除路径"""
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
            config_data = self.parent_window.get_config_data()
            github_repos = config_data.get("githubRepoPaths", {})
            if repo_name in github_repos:
                paths = github_repos[repo_name]
                if path in paths:
                    paths.remove(path)

                    self.parent_window.set_config_data(config_data)
                    self.parent_window.save_config_to_file()
                    self.load_data(config_data)
                    self.on_repo_selected()
                    self.parent_window.raw_config_tab.load_data(config_data)

                    QMessageBox.information(self, "成功", "路径已删除!")
