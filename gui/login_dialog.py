"""
登录对话框
提供二维码登录和手机号验证码登录的GUI界面
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import asyncio
from typing import Optional, Callable
from pathlib import Path

from core.auth import AuthManager, LoginMethod
from core.browser import browser_manager
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginDialog:
    """登录对话框"""

    def __init__(self, parent, auth_manager: AuthManager, loop=None):
        """
        初始化登录对话框

        Args:
            parent: 父窗口
            auth_manager: 认证管理器实例
            loop: asyncio事件循环
        """
        self.dialog = tk.Toplevel(parent)
        self.auth_manager = auth_manager
        self.loop = loop
        self.login_method = tk.StringVar(value='qrcode')
        self.is_logged_in = False
        self.login_future: Optional[asyncio.Future] = None
        self.page = None  # 用于保存浏览器页面

        self._create_widgets()

        # 设置为模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        """创建GUI组件"""
        self.dialog.title("登录小红书创作者平台")
        self.dialog.resizable(False, False)

        # 主容器
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="登录小红书创作者平台",
            font=('Microsoft YaHei', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))

        # 登录方式选择
        method_frame = ttk.LabelFrame(main_frame, text="选择登录方式", padding="10")
        method_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Radiobutton(
            method_frame,
            text="二维码登录（推荐）",
            variable=self.login_method,
            value='qrcode',
            command=self._on_method_changed
        ).pack(anchor=tk.W, pady=5)

        ttk.Radiobutton(
            method_frame,
            text="手机号+验证码登录",
            variable=self.login_method,
            value='sms',
            command=self._on_method_changed
        ).pack(anchor=tk.W, pady=5)

        # 动态区域容器
        self.dynamic_frame = ttk.Frame(main_frame)
        self.dynamic_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 初始化显示二维码登录界面
        self._show_qrcode_login()

        # 状态显示
        self.status_label = ttk.Label(
            main_frame,
            text="请选择登录方式",
            font=('Microsoft YaHei', 9)
        )
        self.status_label.pack(pady=(0, 10))

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        self.login_button = ttk.Button(
            button_frame,
            text="开始登录",
            command=self._start_login
        )
        self.login_button.pack(side=tk.RIGHT, padx=(0, 5))

        ttk.Button(
            button_frame,
            text="取消",
            command=self._cancel
        ).pack(side=tk.RIGHT)

    def _on_method_changed(self):
        """登录方式改变时的回调"""
        method = self.login_method.get()

        # 清空动态区域
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

        if method == 'qrcode':
            self._show_qrcode_login()
        else:
            self._show_sms_login()

    def _show_qrcode_login(self):
        """显示二维码登录界面"""
        container = ttk.Frame(self.dynamic_frame)
        container.pack(fill=tk.BOTH, expand=True)

        # 二维码显示区域
        qrcode_frame = ttk.Frame(container)
        qrcode_frame.pack(pady=20)

        # 创建Label用于显示二维码图片
        self.qrcode_label = tk.Label(
            qrcode_frame,
            text="二维码区域\n（点击开始登录后显示）",
            font=('Microsoft YaHei', 10),
            relief=tk.RIDGE,
            bd=2,
            padx=20,
            pady=20,
            width=30,
            height=10
        )
        self.qrcode_label.pack()

        # 提示信息
        hint_label = ttk.Label(
            container,
            text="使用小红书APP扫描二维码登录",
            font=('Microsoft YaHei', 9)
        )
        hint_label.pack()

    def _show_sms_login(self):
        """显示手机号验证码登录界面"""
        container = ttk.Frame(self.dynamic_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10)

        # 手机号输入
        phone_frame = ttk.Frame(container)
        phone_frame.pack(fill=tk.X, pady=10)

        ttk.Label(phone_frame, text="手机号：").pack(side=tk.LEFT)

        self.phone_entry = ttk.Entry(phone_frame, width=25)
        self.phone_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # 验证码输入
        code_frame = ttk.Frame(container)
        code_frame.pack(fill=tk.X, pady=10)

        ttk.Label(code_frame, text="验证码：").pack(side=tk.LEFT)

        self.code_entry = ttk.Entry(code_frame, width=25)
        self.code_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # 提示信息
        hint_label = ttk.Label(
            container,
            text="请输入手机号，点击获取验证码后",
            font=('Microsoft YaHei', 9),
            foreground='gray'
        )
        hint_label.pack(pady=(10, 0))

    def _update_status(self, message: str):
        """更新状态显示"""
        self.status_label.config(text=message)
        self.dialog.update_idletasks()

    def _start_login(self):
        """开始登录"""
        method = self.login_method.get()

        if method == 'qrcode':
            # 创建异步任务
            if self.loop:
                asyncio.run_coroutine_threadsafe(self._start_qrcode_login(), self.loop)
            else:
                # 如果没有提供loop，使用ensure_future
                asyncio.ensure_future(self._start_qrcode_login())
        else:
            self._start_sms_login()

    async def _start_qrcode_login(self):
        """开始二维码登录"""
        try:
            self._update_status("正在启动浏览器...")
            self.login_button.config(state=tk.DISABLED)

            # 启动浏览器并获取页面
            if not self.page:
                await browser_manager.launch()
                await browser_manager.create_context()
                self.page = await browser_manager.new_page()

            self._update_status("正在打开登录页面...")

            # 导航到登录页面
            await self.page.goto(Config.LOGIN_URL)
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)

            # 尝试切换到二维码登录tab
            self._update_status("正在切换到二维码登录...")
            try:
                qrcode_tab_selectors = [
                    'a:has-text("扫码登录")',
                    'a:has-text("二维码登录")',
                    '[class*="tab"]:has-text("扫码")',
                    'div:has-text("扫码登录")',
                    'button:has-text("扫码登录")',
                ]

                clicked = False
                for selector in qrcode_tab_selectors:
                    try:
                        element = await self.page.wait_for_selector(selector, timeout=2000)
                        if element and await element.is_visible():
                            await element.click()
                            clicked = True
                            logger.info(f"成功切换到二维码登录: {selector}")
                            break
                    except:
                        continue

                if not clicked:
                    logger.info("未找到切换按钮，可能已显示二维码")

                await asyncio.sleep(2)

            except Exception as e:
                logger.info(f"切换操作: {e}")

            # 更新UI提示
            self._update_status("✅ 浏览器已打开")

            # 更新二维码区域显示提示
            self.qrcode_label.config(
                text="✅ 浏览器窗口已打开\n\n请在浏览器窗口中\n使用小红书APP扫码登录\n\n登录完成后自动关闭"
            )
            self.qrcode_label.config(foreground='green')

            # 继续执行登录检查
            self.login_future = asyncio.ensure_future(self._do_qrcode_login())
            self.login_future.add_done_callback(self._on_login_complete)

        except Exception as e:
            logger.error(f"二维码登录出错: {e}")
            self._update_status(f"登录出错: {e}")
            self.login_button.config(state=tk.NORMAL)
            self.is_logged_in = False

    def _display_qrcode_from_url(self, url: str):
        """从URL加载并显示二维码"""
        try:
            import requests
            from io import BytesIO

            # 下载图片
            response = requests.get(url, timeout=10)
            image_data = BytesIO(response.content)

            # 打开并显示图片
            image = Image.open(image_data)
            image = image.resize((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            self.qrcode_label.config(image=photo, text="")
            self.qrcode_label.image = photo  # 保持引用

        except Exception as e:
            logger.error(f"加载二维码图片失败: {e}")

    def _display_qrcode_image(self, image_path: Path):
        """从文件加载并显示二维码"""
        try:
            if not image_path.exists():
                logger.warning(f"二维码图片不存在: {image_path}")
                self.qrcode_label.config(text=f"二维码图片未找到\n{image_path}")
                return

            logger.info(f"正在加载二维码图片: {image_path}")

            # 打开图片
            image = Image.open(image_path)
            logger.info(f"图片大小: {image.size}")

            # 调整大小
            image = image.resize((200, 200), Image.Resampling.LANCZOS)

            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(image)
            logger.info("PhotoImage创建成功")

            # 在主线程中更新GUI
            def update_gui():
                try:
                    self.qrcode_label.config(image=photo, text="")
                    self.qrcode_label.image = photo  # 保持引用，防止被垃圾回收
                    logger.info("二维码图片已显示")
                except Exception as e:
                    logger.error(f"更新GUI失败: {e}")

            self.dialog.after(0, update_gui)

        except Exception as e:
            logger.error(f"显示二维码图片失败: {e}", exc_info=True)
            self.qrcode_label.config(text=f"加载失败\n{str(e)}")

    def _start_sms_login(self):
        """开始手机号验证码登录"""
        phone = self.phone_entry.get().strip()
        code = self.code_entry.get().strip()

        if not phone or not code:
            messagebox.showwarning("输入错误", "请输入手机号和验证码")
            return

        self._update_status(f"正在登录（{phone}）...")
        self.login_button.config(state=tk.DISABLED)

        # 创建异步任务
        self.login_future = asyncio.ensure_future(self._do_sms_login(phone, code))

        # 设置完成回调
        self.login_future.add_done_callback(self._on_login_complete)

    async def _do_qrcode_login(self):
        """执行二维码登录"""
        try:
            self.is_logged_in = await self.auth_manager.login(
                method=LoginMethod.QRCODE,
                status_callback=self._update_status
            )
        except Exception as e:
            logger.error(f"二维码登录出错: {e}")
            self._update_status(f"登录出错: {e}")
            self.is_logged_in = False

    async def _do_sms_login(self, phone: str, code: str):
        """执行手机号验证码登录"""
        try:
            self.is_logged_in = await self.auth_manager.login(
                method=LoginMethod.SMS,
                phone=phone,
                code=code,
                status_callback=self._update_status
            )
        except Exception as e:
            logger.error(f"手机号登录出错: {e}")
            self._update_status(f"登录出错: {e}")
            self.is_logged_in = False

    def _on_login_complete(self, future):
        """登录完成回调"""
        try:
            future.result()  # 获取结果或异常
        except Exception as e:
            logger.error(f"登录任务出错: {e}")

        self.login_button.config(state=tk.NORMAL)

        if self.is_logged_in:
            self._update_status("登录成功！")
            messagebox.showinfo("成功", "登录成功！")
            self.dialog.destroy()
        else:
            self._update_status("登录失败，请重试")

    def _cancel(self):
        """取消登录"""
        if self.login_future and not self.login_future.done():
            self.login_future.cancel()

        self.dialog.destroy()

    def show(self):
        """
        显示对话框并等待结果

        Returns:
            bool: 是否登录成功
        """
        self.dialog.wait_window()
        return self.is_logged_in
