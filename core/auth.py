"""
登录认证模块
处理小红书创作者平台的登录流程
"""
import asyncio
from enum import Enum
from typing import Optional, Callable
from playwright.async_api import Page

from config import Config
from core.browser import browser_manager
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginMethod(Enum):
    """登录方式枚举"""
    QRCODE = 'qrcode'  # 二维码登录
    SMS = 'sms'        # 手机号+验证码登录


class AuthManager:
    """登录认证管理器"""

    def __init__(self):
        self.page: Optional[Page] = None
        self.login_method = LoginMethod.QRCODE

    async def login(
        self,
        method: LoginMethod = LoginMethod.QRCODE,
        phone: Optional[str] = None,
        code: Optional[str] = None,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        执行登录流程

        Args:
            method: 登录方式（二维码或验证码）
            phone: 手机号（仅SMS登录需要）
            code: 验证码（仅SMS登录需要）
            status_callback: 状态回调函数，用于向GUI报告进度

        Returns:
            bool: 登录是否成功
        """
        self.login_method = method

        def update_status(msg: str):
            """更新状态"""
            logger.info(msg)
            if status_callback:
                status_callback(msg)

        try:
            update_status("正在创建浏览器页面...")
            self.page = await browser_manager.new_page()

            update_status("正在导航到登录页面...")
            await self.page.goto(Config.LOGIN_URL)
            await self.page.wait_for_load_state('networkidle')

            update_status("等待登录页面加载...")
            # 等待登录页面加载
            await asyncio.sleep(1)

            # 根据登录方式处理
            if method == LoginMethod.QRCODE:
                success = await self._login_by_qrcode(update_status)
            elif method == LoginMethod.SMS:
                if not phone or not code:
                    update_status("错误：手机号和验证码不能为空")
                    return False
                success = await self._login_by_sms(phone, code, update_status)
            else:
                update_status(f"错误：不支持的登录方式 {method}")
                return False

            if success:
                update_status("登录成功！正在保存会话...")
                await browser_manager.save_session()
                update_status("会话保存完成")
                return True
            else:
                update_status("登录失败")
                return False

        except Exception as e:
            update_status(f"登录过程出错: {str(e)}")
            logger.error(f"登录出错: {e}", exc_info=True)
            return False

    async def _login_by_qrcode(self, status_callback: Callable[[str], None]) -> bool:
        """
        二维码登录

        Args:
            status_callback: 状态回调函数

        Returns:
            bool: 是否登录成功
        """
        try:
            status_callback("二维码登录模式")
            status_callback("请在手机上打开小红书APP扫描二维码登录")

            # 等待二维码出现
            logger.debug("等待二维码元素...")
            await self.page.wait_for_selector('img[src*="qrcode"], .qrcode, canvas', timeout=10000)
            status_callback("二维码已显示，请使用小红书APP扫码")

            # 等待登录成功（URL变化或出现用户头像）
            logger.debug("等待用户扫码登录...")

            # 方式1: 等待URL跳转到主页
            try:
                await self.page.wait_for_url(
                    f"{Config.CREATOR_PLATFORM_URL}/**",
                    timeout=60000  # 等待60秒
                )
                status_callback("检测到登录成功（URL跳转）")
                return True
            except:
                logger.debug("URL未跳转，尝试检测登录元素")

            # 方式2: 检测页面上是否有用户头像等登录标识
            try:
                await self.page.wait_for_selector('.user-avatar, .avatar, [class*="user"]', timeout=3000)
                status_callback("检测到登录成功（用户头像）")
                return True
            except:
                logger.debug("未检测到用户头像")

            # 方式3: 检测特定登录成功标识
            try:
                # 检查是否有退出登录按钮等
                await self.page.wait_for_selector('[class*="logout"], [class*="exit"]', timeout=3000)
                status_callback("检测到登录成功（退出按钮）")
                return True
            except:
                pass

            status_callback("登录超时或失败，请重试")
            return False

        except Exception as e:
            status_callback(f"二维码登录失败: {str(e)}")
            logger.error(f"二维码登录失败: {e}", exc_info=True)
            return False

    async def _login_by_sms(
        self,
        phone: str,
        code: str,
        status_callback: Callable[[str], None]
    ) -> bool:
        """
        手机号+验证码登录

        Args:
            phone: 手机号
            code: 验证码
            status_callback: 状态回调函数

        Returns:
            bool: 是否登录成功
        """
        try:
            status_callback("手机号验证码登录模式")

            # 点击切换到手机号登录（如果需要）
            try:
                # 尝试查找手机号登录的tab或按钮
                sms_tab = self.page.get_by_text('手机号登录').or_(
                    self.page.query_selector('.login-tab-sms')
                ).or_(
                    self.page.query_selector('[data-method="sms"]')
                )

                if await sms_tab.is_visible():
                    await sms_tab.click()
                    await asyncio.sleep(0.5)
                    status_callback("已切换到手机号登录")
            except:
                logger.debug("可能已经在手机号登录页面，或无法找到切换按钮")

            # 输入手机号
            status_callback("正在输入手机号...")
            phone_input = self.page.wait_for_selector('input[placeholder*="手机号"], input[type="tel"]', timeout=5000)
            await phone_input.fill(phone)
            await asyncio.sleep(0.3)

            # 点击获取验证码（如果需要）
            try:
                get_code_btn = self.page.query_selector('button:has-text("获取验证码"), .get-code-btn')
                if get_code_btn and await get_code_btn.is_visible():
                    status_callback("点击获取验证码按钮...")
                    await get_code_btn.click()
                    await asyncio.sleep(1)
            except:
                logger.debug("可能不需要点击获取验证码，或无法找到按钮")

            # 输入验证码
            status_callback("正在输入验证码...")
            code_input = self.page.wait_for_selector('input[placeholder*="验证码"]', timeout=5000)
            await code_input.fill(code)
            await asyncio.sleep(0.3)

            # 点击登录按钮
            status_callback("正在点击登录按钮...")
            login_btn = self.page.wait_for_selector('button:has-text("登录"), .login-btn, button[type="submit"]', timeout=5000)
            await login_btn.click()

            # 等待登录结果
            status_callback("等待登录结果...")

            # 等待URL跳转或登录标识
            try:
                await self.page.wait_for_url(
                    f"{Config.CREATOR_PLATFORM_URL}/**",
                    timeout=10000
                )
                status_callback("登录成功！")
                return True
            except:
                # 检查是否有错误提示
                try:
                    error_msg = await self.page.query_selector('.error-message, .toast-error').inner_text()
                    status_callback(f"登录失败: {error_msg}")
                    return False
                except:
                    pass

            # 最后尝试检测登录标识
            try:
                await self.page.wait_for_selector('.user-avatar, .avatar', timeout=3000)
                status_callback("登录成功！")
                return True
            except:
                pass

            status_callback("登录失败，请检查手机号和验证码")
            return False

        except Exception as e:
            status_callback(f"手机号登录失败: {str(e)}")
            logger.error(f"手机号登录失败: {e}", exc_info=True)
            return False

    async def check_login_status(self) -> bool:
        """
        检查当前是否已登录

        Returns:
            bool: 是否已登录
        """
        try:
            if not self.page:
                self.page = await browser_manager.new_page()

            await self.page.goto(Config.CREATOR_PLATFORM_URL)
            await self.page.wait_for_load_state('networkidle')

            # 检查是否有登录标识
            is_logged_in = await browser_manager.is_logged_in(self.page)

            if is_logged_in:
                logger.info("当前已登录")
                return True
            else:
                logger.info("当前未登录")
                return False

        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False

    async def logout(self):
        """退出登录"""
        try:
            if self.page:
                # 尝试点击退出登录按钮
                try:
                    logout_btn = self.page.query_selector('[class*="logout"], [class*="exit"]')
                    if logout_btn:
                        await logout_btn.click()
                        await asyncio.sleep(1)
                except:
                    pass

                # 清除会话文件
                if Config.SESSION_FILE.exists():
                    Config.SESSION_FILE.unlink()
                    logger.info("已删除会话文件")

            logger.info("退出登录成功")

        except Exception as e:
            logger.error(f"退出登录失败: {e}")
