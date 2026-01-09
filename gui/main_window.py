"""
主窗口GUI
小红书创作者平台数据抓取工具的主界面
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
from typing import Optional
import threading

from config import Config
from core.auth import AuthManager
from core.browser import browser_manager
from modules.notes_exporter import NotesExporter
from modules.followers_scraper import FollowersScraper
from gui.login_dialog import LoginDialog
from utils.logger import get_logger, Logger

logger = get_logger(__name__)


class MainWindow:
    """主窗口"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("小红书创作者平台数据抓取工具")
        self.root.geometry("900x700")

        # 核心组件
        self.auth_manager = AuthManager()
        self.notes_exporter = NotesExporter()
        self.followers_scraper = FollowersScraper()

        # 登录状态
        self.is_logged_in = False

        # 事件循环（在单独线程中运行）
        self.loop = None
        self.loop_thread = None

        # 创建GUI
        self._create_widgets()

        # 设置日志回调
        Logger.add_gui_callback(self._append_log)

        # 启动事件循环
        self._start_event_loop()

        # 延迟1秒后自动检查登录状态
        self.root.after(1000, self._auto_check_login_status)

    def _create_widgets(self):
        """创建GUI组件"""
        # 1. 顶部标题栏
        self._create_title_bar()

        # 2. 登录状态区域
        self._create_login_area()

        # 3. 功能标签页
        self._create_notebook()

        # 4. 日志区域
        self._create_log_area()

        # 5. 底部状态栏
        self._create_status_bar()

    def _create_title_bar(self):
        """创建标题栏"""
        title_frame = tk.Frame(self.root, bg='#FF2442', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="小红书创作者平台数据抓取工具",
            font=('Microsoft YaHei', 16, 'bold'),
            bg='#FF2442',
            fg='white'
        )
        title_label.pack(pady=15)

    def _create_login_area(self):
        """创建登录状态区域"""
        login_frame = ttk.LabelFrame(self.root, text="登录状态", padding="10")
        login_frame.pack(fill=tk.X, padx=20, pady=(10, 10))

        # 状态标签容器
        status_container = ttk.Frame(login_frame)
        status_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(status_container, text="当前状态：").pack(side=tk.LEFT)

        self.login_status_label = ttk.Label(
            status_container,
            text="未登录",
            foreground='red',
            font=('Microsoft YaHei', 10, 'bold')
        )
        self.login_status_label.pack(side=tk.LEFT, padx=(5, 0))

        # 登录按钮
        self.login_button = ttk.Button(
            login_frame,
            text="登录账号",
            command=self._open_login_dialog
        )
        self.login_button.pack(side=tk.RIGHT)

    def _create_notebook(self):
        """创建功能标签页"""
        notebook_frame = ttk.Frame(self.root)
        notebook_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 笔记数据导出标签页
        notes_tab = ttk.Frame(self.notebook)
        self.notebook.add(notes_tab, text="笔记数据导出")
        self._create_notes_tab(notes_tab)

        # 粉丝数据抓取标签页
        followers_tab = ttk.Frame(self.notebook)
        self.notebook.add(followers_tab, text="粉丝数据抓取")
        self._create_followers_tab(followers_tab)

    def _create_notes_tab(self, parent):
        """创建笔记数据导出标签页"""
        container = ttk.Frame(parent, padding="20")
        container.pack(fill=tk.BOTH, expand=True)

        # 说明文字
        info_label = ttk.Label(
            container,
            text="导出小红书创作者平台的内容分析-笔记数据",
            font=('Microsoft YaHei', 10)
        )
        info_label.pack(pady=(0, 20))

        # 日期范围选择（可选）
        date_frame = ttk.LabelFrame(container, text="日期范围（可选）", padding="10")
        date_frame.pack(fill=tk.X, pady=(0, 20))

        date_input_frame = ttk.Frame(date_frame)
        date_input_frame.pack(fill=tk.X)

        ttk.Label(date_input_frame, text="开始日期：").pack(side=tk.LEFT)

        self.notes_start_date = ttk.Entry(date_input_frame, width=15)
        self.notes_start_date.pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(date_input_frame, text="结束日期：").pack(side=tk.LEFT)

        self.notes_end_date = ttk.Entry(date_input_frame, width=15)
        self.notes_end_date.pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(
            date_frame,
            text="提示：留空表示导出全部数据，格式：YYYY-MM-DD",
            font=('Microsoft YaHei', 8),
            foreground='gray'
        ).pack(pady=(5, 0))

        # 导出按钮
        button_frame = ttk.Frame(container)
        button_frame.pack(pady=(0, 20))

        self.export_notes_button = ttk.Button(
            button_frame,
            text="开始导出笔记数据",
            command=self._export_notes,
            width=25
        )
        self.export_notes_button.pack()

        # 进度条
        self.notes_progress = ttk.Progressbar(
            container,
            mode='determinate',
            length=400
        )
        self.notes_progress.pack(pady=(0, 10))

        # 状态显示
        self.notes_status_label = ttk.Label(
            container,
            text="",
            font=('Microsoft YaHei', 9)
        )
        self.notes_status_label.pack()

    def _create_followers_tab(self, parent):
        """创建粉丝数据抓取标签页"""
        container = ttk.Frame(parent, padding="20")
        container.pack(fill=tk.BOTH, expand=True)

        # 说明文字
        info_label = ttk.Label(
            container,
            text="抓取粉丝数据（每日新增、掉丝、总数）",
            font=('Microsoft YaHei', 10)
        )
        info_label.pack(pady=(0, 20))

        # 天数选择
        days_frame = ttk.LabelFrame(container, text="抓取天数", padding="10")
        days_frame.pack(fill=tk.X, pady=(0, 20))

        days_input_frame = ttk.Frame(days_frame)
        days_input_frame.pack(fill=tk.X)

        ttk.Label(days_input_frame, text="最近").pack(side=tk.LEFT)

        self.followers_days = ttk.Spinbox(
            days_input_frame,
            from_=1,
            to=90,
            width=10,
            font=('Microsoft YaHei', 10)
        )
        self.followers_days.set(Config.DEFAULT_FOLLOWER_DAYS)
        self.followers_days.pack(side=tk.LEFT, padx=(5, 5))

        ttk.Label(days_input_frame, text="天的数据").pack(side=tk.LEFT)

        # 抓取按钮
        button_frame = ttk.Frame(container)
        button_frame.pack(pady=(0, 20))

        self.scrape_followers_button = ttk.Button(
            button_frame,
            text="开始抓取粉丝数据",
            command=self._scrape_followers,
            width=25
        )
        self.scrape_followers_button.pack()

        # 进度条
        self.followers_progress = ttk.Progressbar(
            container,
            mode='determinate',
            length=400
        )
        self.followers_progress.pack(pady=(0, 10))

        # 状态显示
        self.followers_status_label = ttk.Label(
            container,
            text="",
            font=('Microsoft YaHei', 9)
        )
        self.followers_status_label.pack()

    def _create_log_area(self):
        """创建日志区域"""
        log_frame = ttk.LabelFrame(self.root, text="运行日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=('Consolas', 9),
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _create_status_bar(self):
        """创建底部状态栏"""
        status_bar = ttk.Frame(self.root)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(
            status_bar,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, side=tk.LEFT)

        version_label = ttk.Label(
            status_bar,
            text="v1.0.0",
            relief=tk.SUNKEN
        )
        version_label.pack(side=tk.RIGHT)

    def _start_event_loop(self):
        """在单独线程中启动事件循环"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()
        logger.info("事件循环已启动")

    def _run_async(self, coro):
        """在事件循环中运行异步任务"""
        if self.loop:
            asyncio.run_coroutine_threadsafe(coro, self.loop)

    def _auto_check_login_status(self):
        """自动检查登录状态"""
        # 检查会话文件是否存在
        if not Config.SESSION_FILE.exists():
            logger.info("未找到会话文件，保持未登录状态")
            return

        logger.info("发现会话文件，正在检查登录状态...")
        self._update_status("正在检查登录状态...")

        # 启动异步检查任务
        self._run_async(self._do_auto_check_login())

    async def _do_auto_check_login(self):
        """执行自动登录检查"""
        try:
            # 启动浏览器并加载会话
            await browser_manager.launch()
            await browser_manager.create_context()
            page = await browser_manager.new_page()

            # 导航到主页检查登录状态
            logger.info("正在导航到主页检查登录状态...")
            await page.goto(Config.CREATOR_PLATFORM_URL, wait_until='domcontentloaded')
            await asyncio.sleep(2)

            # 检查是否已登录
            is_logged_in = False

            # 方法1: 检查URL
            if Config.CREATOR_PLATFORM_URL in page.url and '/login' not in page.url:
                is_logged_in = True
                logger.info("检测到已登录（URL检查）")

            # 方法2: 检查页面元素
            elif await browser_manager.is_logged_in(page):
                is_logged_in = True
                logger.info("检测到已登录（页面元素检查）")

            # 更新界面
            if is_logged_in:
                logger.info("自动登录检查：已登录")
                self.root.after(0, lambda: self._on_login_complete(True, show_message=False))
            else:
                logger.info("自动登录检查：未登录")
                self.root.after(0, lambda: self._on_login_complete(False, show_message=False))

        except Exception as e:
            logger.error(f"自动检查登录状态失败: {e}")
            self.root.after(0, lambda: self._update_status("登录状态检查失败"))

    def _open_login_dialog(self):
        """打开浏览器进行登录"""
        if self.is_logged_in:
            messagebox.showinfo("提示", "您已经登录了！")
            return

        # 创建异步任务
        self._run_async(self._do_login())

    async def _do_login(self):
        """执行登录流程"""
        try:
            def update_progress(msg: str):
                self._update_status(msg)

            # 启动浏览器
            update_progress("正在启动浏览器...")

            await browser_manager.launch()
            await browser_manager.create_context()
            page = await browser_manager.new_page()

            update_progress("正在打开登录页面...")

            # 导航到登录页面
            await page.goto(Config.LOGIN_URL)
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)  # 等待页面完全加载

            # 立即检查是否已经登录
            update_progress("正在检查登录状态...")
            is_already_logged_in = False

            try:
                # 检查URL
                if Config.CREATOR_PLATFORM_URL in page.url and '/login' not in page.url:
                    is_already_logged_in = True
                    logger.info("检测到已登录（URL检查）")
                elif await browser_manager.is_logged_in(page):
                    is_already_logged_in = True
                    logger.info("检测到已登录（页面元素检查）")
            except Exception as e:
                logger.info(f"登录状态检查: {e}")

            if is_already_logged_in:
                update_progress("✅ 检测到已登录，保存会话...")
                await browser_manager.save_session()
                self.root.after(0, lambda: self._on_login_complete(True))
                return

            # 未登录，提示用户登录
            update_progress("✅ 浏览器已打开，请在浏览器中登录（扫码或手机号）")

            # 等待用户登录（最多等待2分钟）
            for i in range(24):  # 24 * 5秒 = 120秒
                await asyncio.sleep(5)

                # 检查是否登录成功
                try:
                    # 检查URL是否跳转到主页
                    if Config.CREATOR_PLATFORM_URL in page.url and '/login' not in page.url:
                        update_progress("✅ 登录成功！正在保存会话...")
                        await browser_manager.save_session()
                        break

                    # 检查是否有登录标识
                    if await browser_manager.is_logged_in(page):
                        update_progress("✅ 登录成功！正在保存会话...")
                        await browser_manager.save_session()
                        break

                except:
                    continue

            # 更新登录状态
            self.root.after(0, lambda: self._on_login_complete(True))

        except Exception as e:
            error_msg = str(e)
            update_progress(f"登录过程出错: {error_msg}")
            self.root.after(0, lambda msg=error_msg: self._on_login_complete(False, msg))

    def _on_login_complete(self, success: bool, error_msg: str = None, show_message: bool = True):
        """
        登录完成回调

        Args:
            success: 是否登录成功
            error_msg: 错误消息
            show_message: 是否显示提示框（自动检查时不显示）
        """
        if success:
            self.is_logged_in = True
            self.login_status_label.config(
                text="已登录",
                foreground='green'
            )
            self._update_status("登录成功，可以开始导出数据")
            if show_message:
                messagebox.showinfo("成功", "登录成功！")
        else:
            self.is_logged_in = False
            self.login_status_label.config(
                text="未登录",
                foreground='red'
            )
            if error_msg and show_message:
                messagebox.showerror("失败", f"登录失败：\n{error_msg}")

    def _export_notes(self):
        """导出笔记数据"""
        if not self.is_logged_in:
            messagebox.showwarning("未登录", "请先登录账号")
            return

        # 获取日期范围
        start_date = self.notes_start_date.get().strip() or None
        end_date = self.notes_end_date.get().strip() or None

        # 禁用按钮
        self.export_notes_button.config(state=tk.DISABLED)
        self.notes_progress['value'] = 0

        # 启动异步任务
        self._run_async(
            self._do_export_notes(start_date, end_date)
        )

    async def _do_export_notes(self, start_date: Optional[str], end_date: Optional[str]):
        """执行笔记数据导出"""
        try:
            def update_progress(msg: str, progress: int):
                """更新进度"""
                self.root.after(0, lambda: self._update_notes_progress(msg, progress))

            output_path = await self.notes_exporter.export_notes_data(
                start_date=start_date,
                end_date=end_date,
                progress_callback=update_progress
            )

            self.root.after(0, lambda: self._on_notes_export_complete(output_path, None))

        except Exception as e:
            error = e
            self.root.after(0, lambda: self._on_notes_export_complete(None, error))

    def _update_notes_progress(self, message: str, progress: int):
        """更新笔记导出进度"""
        self.notes_progress['value'] = progress
        self.notes_status_label.config(text=message)
        self.root.update_idletasks()

    def _on_notes_export_complete(self, output_path: Optional[str], error: Optional[Exception]):
        """笔记导出完成回调"""
        self.export_notes_button.config(state=tk.NORMAL)

        if error:
            messagebox.showerror("导出失败", f"导出笔记数据失败：\n{str(error)}")
            self.notes_status_label.config(text="导出失败")
        else:
            messagebox.showinfo("导出成功", f"笔记数据已导出到：\n{output_path}")
            self.notes_status_label.config(text="导出成功")
            self.notes_progress['value'] = 100

    def _scrape_followers(self):
        """抓取粉丝数据"""
        if not self.is_logged_in:
            messagebox.showwarning("未登录", "请先登录账号")
            return

        # 获取天数
        try:
            days = int(self.followers_days.get())
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的天数")
            return

        # 禁用按钮
        self.scrape_followers_button.config(state=tk.DISABLED)
        self.followers_progress['value'] = 0

        # 启动异步任务
        self._run_async(
            self._do_scrape_followers(days)
        )

    async def _do_scrape_followers(self, days: int):
        """执行粉丝数据抓取"""
        try:
            def update_progress(msg: str, progress: int):
                """更新进度"""
                self.root.after(0, lambda: self._update_followers_progress(msg, progress))

            output_path = await self.followers_scraper.scrape_followers_data(
                days=days,
                progress_callback=update_progress
            )

            self.root.after(0, lambda: self._on_followers_scrape_complete(output_path, None))

        except Exception as e:
            error = e
            self.root.after(0, lambda: self._on_followers_scrape_complete(None, error))

    def _update_followers_progress(self, message: str, progress: int):
        """更新粉丝抓取进度"""
        self.followers_progress['value'] = progress
        self.followers_status_label.config(text=message)
        self.root.update_idletasks()

    def _on_followers_scrape_complete(self, output_path: Optional[str], error: Optional[Exception]):
        """粉丝抓取完成回调"""
        self.scrape_followers_button.config(state=tk.NORMAL)

        if error:
            messagebox.showerror("抓取失败", f"抓取粉丝数据失败：\n{str(error)}")
            self.followers_status_label.config(text="抓取失败")
        else:
            messagebox.showinfo("抓取成功", f"粉丝数据已保存到：\n{output_path}")
            self.followers_status_label.config(text="抓取成功")
            self.followers_progress['value'] = 100

    def _append_log(self, message: str):
        """追加日志到日志区域"""
        def _do_append():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + '\n')
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

        self.root.after(0, _do_append)

    def _update_status(self, message: str):
        """更新底部状态栏"""
        self.status_label.config(text=message)

    def run(self):
        """运行主窗口"""
        try:
            logger.info("应用程序启动")
            self.root.mainloop()
        finally:
            # 清理资源
            if self.loop:
                self.loop.call_soon_threadsafe(self.loop.stop)
            logger.info("应用程序退出")
