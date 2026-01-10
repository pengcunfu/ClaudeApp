"""
Claude Configuration Manager
Claude 配置管理器主程序
"""
import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import ClaudeConfigGUI


def main():
    """主函数"""
    # 创建应用
    app = QApplication(sys.argv)

    # 设置 Windows Vista 风格
    app.setStyle("WindowsVista")

    # 创建并显示主窗口
    window = ClaudeConfigGUI()
    window.show()

    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
