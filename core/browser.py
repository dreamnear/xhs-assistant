"""
浏览器管理模块
使用单例模式管理Playwright浏览器实例
"""
import asyncio
import json
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class BrowserManager:
    """浏览器管理器（单例模式）"""

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._initialized = True
        logger.info("浏览器管理器初始化完成")

    async def launch(self) -> Browser:
        """
        启动浏览器
        """
        if self.browser is not None:
            logger.debug("浏览器已经启动，直接返回")
            return self.browser

        try:
            logger.info(f"正在启动 {Config.BROWSER_TYPE} 浏览器...")

            # 启动Playwright
            self.playwright = await async_playwright().start()

            # 启动浏览器
            launch_options = {
                'headless': Config.HEADLESS,
                'slow_mo': Config.SLOW_MO,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            }

            if Config.BROWSER_TYPE == 'chromium':
                self.browser = await self.playwright.chromium.launch(**launch_options)
            elif Config.BROWSER_TYPE == 'firefox':
                self.browser = await self.playwright.firefox.launch(**launch_options)
            elif Config.BROWSER_TYPE == 'webkit':
                self.browser = await self.playwright.webkit.launch(**launch_options)
            else:
                raise ValueError(f"不支持的浏览器类型: {Config.BROWSER_TYPE}")

            logger.info("浏览器启动成功")

            # 定位浏览器窗口到GUI右侧
            try:
                from utils.window_utils import position_browser_window_right
                # 等待一下让窗口完全显示
                await asyncio.sleep(1)
                position_browser_window_right()
            except Exception as e:
                logger.debug(f"窗口定位失败（非关键错误）: {e}")

            return self.browser

        except Exception as e:
            logger.error(f"浏览器启动失败: {e}")
            raise

    async def create_context(self, load_session: bool = True) -> BrowserContext:
        """
        创建浏览器上下文

        Args:
            load_session: 是否加载已保存的会话
        """
        if self.context is not None:
            logger.debug("浏览器上下文已经存在，直接返回")
            return self.context

        try:
            # 确保浏览器已启动
            if self.browser is None:
                await self.launch()

            # 创建上下文的选项
            context_options = {
                'viewport': {
                    'width': Config.BROWSER_WIDTH,
                    'height': Config.BROWSER_HEIGHT
                },
                'locale': 'zh-CN',
                'timezone_id': 'Asia/Shanghai',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            # 如果需要加载会话且会话文件存在
            if load_session and Config.SESSION_FILE.exists():
                logger.info(f"加载已保存的会话: {Config.SESSION_FILE}")
                try:
                    with open(Config.SESSION_FILE, 'r', encoding='utf-8') as f:
                        storage_state = json.load(f)
                    context_options['storage_state'] = storage_state
                    logger.info("会话加载成功")
                except Exception as e:
                    logger.warning(f"会话加载失败: {e}，将创建新会话")

            # 创建上下文
            self.context = await self.browser.new_context(**context_options)
            logger.info("浏览器上下文创建成功")

            return self.context

        except Exception as e:
            logger.error(f"创建浏览器上下文失败: {e}")
            raise

    async def new_page(self) -> Page:
        """
        创建新页面
        """
        if self.context is None:
            await self.create_context()

        page = await self.context.new_page()
        page.set_default_timeout(Config.PAGE_TIMEOUT)
        logger.debug("新页面创建成功")

        return page

    async def save_session(self):
        """保存当前会话状态"""
        if self.context is None:
            logger.warning("没有活动的浏览器上下文，无法保存会话")
            return

        try:
            # 获取存储状态
            storage_state = await self.context.storage_state()

            # 确保目录存在
            Config.SESSION_DIR.mkdir(parents=True, exist_ok=True)

            # 保存到文件
            with open(Config.SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(storage_state, f, ensure_ascii=False, indent=2)

            logger.info(f"会话已保存到: {Config.SESSION_FILE}")

        except Exception as e:
            logger.error(f"保存会话失败: {e}")

    async def close_context(self):
        """关闭浏览器上下文"""
        if self.context is not None:
            try:
                await self.context.close()
                self.context = None
                logger.info("浏览器上下文已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器上下文失败: {e}")

    async def close_browser(self):
        """关闭浏览器"""
        try:
            # 先关闭上下文
            await self.close_context()

            # 再关闭浏览器
            if self.browser is not None:
                await self.browser.close()
                self.browser = None
                logger.info("浏览器已关闭")

            # 停止Playwright
            if self.playwright is not None:
                await self.playwright.stop()
                self.playwright = None

        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")

    async def is_logged_in(self, page: Page) -> bool:
        """
        检查是否已登录
        通过检测页面上是否有用户头像等登录标识
        """
        try:
            await page.wait_for_selector('.user-avatar, .avatar, [class*="user"]', timeout=3000)
            return True
        except:
            return False

    def set_logger_callback(self, callback):
        """
        设置日志回调函数（用于GUI显示）
        """
        logger.add_callback(callback)


# 全局浏览器管理器实例
browser_manager = BrowserManager()
