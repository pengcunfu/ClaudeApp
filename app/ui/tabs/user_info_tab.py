"""
用户信息标签页
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLabel, QPushButton, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt


class UserInfoTab(QWidget):
    """用户信息标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 用户信息组
        user_group = QGroupBox("用户信息")
        user_layout = QFormLayout(user_group)

        self.user_id_label = QLabel()
        self.user_id_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.user_id_label.setWordWrap(True)
        user_layout.addRow("用户ID:", self.user_id_label)

        self.first_start_label = QLabel()
        user_layout.addRow("首次使用时间:", self.first_start_label)

        self.usage_time_label = QLabel()
        user_layout.addRow("使用时长:", self.usage_time_label)

        layout.addWidget(user_group)

        # 备份与恢复组
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

        # 备份信息
        backup_info = QLabel("提示: 保存配置时会自动创建 .bak 备份文件")
        backup_info.setStyleSheet("color: #666; font-size: 10px;")
        backup_layout.addWidget(backup_info)

        layout.addWidget(backup_group)
        layout.addStretch()

    def load_data(self, config_data):
        """加载数据"""
        user_id = config_data.get("userID", "未知")
        self.user_id_label.setText(user_id)

        first_start = config_data.get("firstStartTime", "")
        if first_start:
            try:
                # 解析 ISO 8601 格式
                start_time = datetime.fromisoformat(first_start.replace('Z', '+00:00'))
                # 转换为本地时区
                local_time = start_time.astimezone()
                formatted = local_time.strftime("%Y-%m-%d %H:%M:%S")
                self.first_start_label.setText(formatted)

                # 计算使用时长
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

    def export_config(self):
        """导出配置"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出配置",
            str(Path.home() / "claude_config_backup.json"),
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )

        if file_path:
            try:
                config_data = self.parent_window.get_config_data()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "成功", f"配置已导出到:\n{file_path}")
                self.parent_window.statusBar().showMessage(f"配置已导出: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")

    def import_config(self):
        """导入配置"""
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

                    # 备份当前配置
                    config_path = self.parent_window.config_path
                    if config_path.exists():
                        backup_path = config_path.with_suffix('.json.bak')
                        shutil.copy2(config_path, backup_path)

                    # 更新配置
                    self.parent_window.set_config_data(imported_data)
                    self.parent_window.save_config_to_file()

                    # 刷新所有视图
                    self.parent_window.refresh_all_views()

                    QMessageBox.information(self, "成功", "配置已导入!")
                    self.parent_window.statusBar().showMessage(f"配置已导入: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"导入失败:\n{str(e)}")

    def reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(
            self, "确认重置",
            "重置配置将删除所有自定义设置!\n此操作不可撤销。\n\n确定要继续吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 创建备份
                config_path = self.parent_window.config_path
                if config_path.exists():
                    backup_path = config_path.with_suffix(f'.json.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                    shutil.copy2(config_path, backup_path)

                # 重置为最小配置
                default_config = {
                    "installMethod": "native",
                    "autoUpdates": False,
                    "mcpServers": {},
                    "githubRepoPaths": {}
                }

                self.parent_window.set_config_data(default_config)
                self.parent_window.save_config_to_file()
                self.parent_window.refresh_all_views()

                QMessageBox.information(self, "成功", "配置已重置为默认值!")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"重置失败:\n{str(e)}")
