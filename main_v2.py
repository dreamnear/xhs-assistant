"""
新版主程序入口
小红书创作者平台数据抓取工具
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window_v2 import MainWindowV2
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """主函数"""
    try:
        # 创建并运行主窗口
        app = MainWindowV2()
        app.run()
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
