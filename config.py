"""
配置管理模块
负责加载和管理项目配置，处理PyInstaller打包后的路径问题
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class Config:
    """项目配置类"""

    # 获取基础路径（处理PyInstaller打包后的情况）
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的路径
        BASE_DIR = Path(sys._MEIPASS)
    else:
        # 开发环境路径
        BASE_DIR = Path(__file__).parent

    # ============================================
    # 路径配置
    # ============================================
    DATA_DIR = BASE_DIR / 'data'
    OUTPUT_DIR = BASE_DIR / os.getenv('OUTPUT_DIR', 'data/output')
    TEMP_DIR = BASE_DIR / 'data/temp'
    SESSION_DIR = BASE_DIR / os.getenv('SESSION_DIR', '.sessions')
    LOG_DIR = BASE_DIR / os.getenv('LOG_DIR', 'logs')
    BROWSERS_DIR = BASE_DIR / 'browsers'

    # ============================================
    # 浏览器配置
    # ============================================
    BROWSER_TYPE = os.getenv('BROWSER_TYPE', 'chromium')
    HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
    BROWSER_WIDTH = int(os.getenv('BROWSER_WIDTH', '1280'))
    BROWSER_HEIGHT = int(os.getenv('BROWSER_HEIGHT', '720'))
    SLOW_MO = int(os.getenv('BROWSER_SLOW_MO', '100'))
    PAGE_TIMEOUT = int(os.getenv('PAGE_TIMEOUT', '30000'))

    # ============================================
    # 日志配置
    # ============================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'

    # ============================================
    # 会话配置
    # ============================================
    SESSION_MAX_AGE = int(os.getenv('SESSION_MAX_AGE', '24'))  # 小时
    SESSION_FILE = SESSION_DIR / 'storage_state.json'

    # ============================================
    # 数据导出配置
    # ============================================
    EXPORT_FORMAT = os.getenv('EXPORT_FORMAT', 'excel')  # csv, excel, both
    ADD_DATE_PREFIX = os.getenv('ADD_DATE_PREFIX', 'true').lower() == 'true'
    CSV_ENCODING = os.getenv('CSV_ENCODING', 'utf-8-sig')
    DEFAULT_FOLLOWER_DAYS = int(os.getenv('DEFAULT_FOLLOWER_DAYS', '30'))

    # ============================================
    # 小红书平台配置
    # ============================================
    CREATOR_PLATFORM_URL = os.getenv('CREATOR_PLATFORM_URL', 'https://creator.xiaohongshu.com')
    LOGIN_URL = f"{CREATOR_PLATFORM_URL}/login"

    # 笔记数据相关URL
    NOTES_DATA_URL = f"{CREATOR_PLATFORM_URL}/statistics/data-analysis"

    # 粉丝数据相关URL
    FOLLOWERS_DATA_URL = f"{CREATOR_PLATFORM_URL}/statistics/fans-data"

    @classmethod
    def init_directories(cls):
        """初始化所有必要的目录"""
        directories = [
            cls.OUTPUT_DIR,
            cls.TEMP_DIR,
            cls.SESSION_DIR,
            cls.LOG_DIR,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_browser_path(cls) -> str:
        """
        获取浏览器路径
        处理PyInstaller打包后的情况
        """
        if getattr(sys, 'frozen', False):
            # PyInstaller打包后
            browser_path = str(cls.BROWSERS_DIR)
        else:
            # 开发环境，使用环境变量或默认路径
            browser_path = os.environ.get(
                'PLAYWRIGHT_BROWSERS_PATH',
                str(cls.BASE_DIR / 'browsers')
            )

        # 设置环境变量
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browser_path

        return browser_path

    @classmethod
    def is_session_valid(cls) -> bool:
        """检查会话是否仍然有效"""
        if not cls.SESSION_FILE.exists():
            return False

        import time
        file_age = time.time() - cls.SESSION_FILE.stat().st_mtime
        max_age_seconds = cls.SESSION_MAX_AGE * 3600  # 转换为秒

        return file_age < max_age_seconds

    @classmethod
    def get_output_filename(cls, prefix: str, extension: str = 'xlsx') -> str:
        """
        生成输出文件名
        格式: prefix_YYYYMMDD_HHMMSS.xlsx
        """
        if not cls.ADD_DATE_PREFIX:
            return f"{prefix}.{extension}"

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"


# 初始化配置
Config.init_directories()
Config.get_browser_path()
