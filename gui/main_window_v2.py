"""
新版主窗口GUI
小红书创作者平台数据抓取工具 - 重新设计的界面
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
from typing import Optional, Dict, Any
import threading

from config import Config
from core.auth import AuthManager
from core.browser import browser_manager
from modules.unified_exporter import UnifiedExporter
from utils.logger import get_logger, Logger

logger = get_logger(__name__)


class MainWindowV2:
    """新版主窗口"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("小红书创作者平台数据抓取工具")
        # 设置窗口位置在左侧，为右侧浏览器留出空间
        self.root.geometry("450x700+20+40")

        # 核心组件
        self.auth_manager = AuthManager()
        self.unified_exporter = UnifiedExporter()

        # 登录状态
        self.is_logged_in = False
        self.browser_visible = True

        # 事件循环（在单独线程中运行）
        self.loop = None
        self.loop_thread = None

        # 导出配置变量
        self.export_notes = tk.BooleanVar(value=True)
        self.export_followers = tk.BooleanVar(value=True)
        self.notes_date_range = tk.StringVar(value="all")  # all, custom
        self.notes_start_date = tk.StringVar(value="")
        self.notes_end_date = tk.StringVar(value="")
        self.followers_days = tk.StringVar(value="30")  # 改为StringVar，用于下拉框

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
        # 创建右侧面板（导出配置）在主窗口中
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._create_main_panel()

    def _create_main_panel(self):
        """创建主面板"""
        # 1. 登录状态区域
        self._create_login_area()

        # 2. 导出配置区域（登录后显示）
        self.export_config_frame = ttk.LabelFrame(
            self.main_frame,
            text="导出配置",
            padding="15"
        )
        self.export_config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self._create_export_config()

        # 3. 日志区域
        self._create_log_area()

        # 4. 底部状态栏
        self._create_status_bar()

        # 初始时隐藏导出配置
        self.export_config_frame.pack_forget()

    def _create_login_area(self):
        """创建登录状态区域"""
        login_frame = ttk.LabelFrame(self.main_frame, text="登录状态", padding="15")
        login_frame.pack(fill=tk.X, pady=(0, 10))

        # 状态标签容器
        status_container = ttk.Frame(login_frame)
        status_container.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(
            status_container,
            text="当前状态：",
            font=('Microsoft YaHei', 11)
        ).pack(side=tk.LEFT)

        self.login_status_label = ttk.Label(
            status_container,
            text="未登录",
            foreground='red',
            font=('Microsoft YaHei', 11, 'bold')
        )
        self.login_status_label.pack(side=tk.LEFT, padx=(10, 0))

        # 登录按钮
        self.login_button = ttk.Button(
            login_frame,
            text="打开浏览器登录",
            command=self._open_login_dialog,
            width=25
        )
        self.login_button.pack()

    def _create_export_config(self):
        """创建导出配置区域"""
        # 使用Grid布局创建表单

        # 1. 笔记数据选项
        notes_frame = ttk.LabelFrame(self.export_config_frame, text="笔记数据", padding="10")
        notes_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        notes_frame.columnconfigure(0, weight=1)

        # 笔记数据复选框
        ttk.Checkbutton(
            notes_frame,
            text="导出笔记数据",
            variable=self.export_notes,
            command=self._on_export_notes_toggle
        ).pack(anchor=tk.W, pady=(0, 10))

        # 日期范围选项
        date_options_frame = ttk.Frame(notes_frame)
        date_options_frame.pack(fill=tk.X, padx=(20, 0))

        ttk.Radiobutton(
            date_options_frame,
            text="导出全部数据",
            variable=self.notes_date_range,
            value="all"
        ).pack(anchor=tk.W, pady=5)

        ttk.Radiobutton(
            date_options_frame,
            text="按日期范围导出",
            variable=self.notes_date_range,
            value="custom",
            command=self._toggle_date_inputs
        ).pack(anchor=tk.W, pady=5)

        # 日期输入框
        self.date_inputs_frame = ttk.Frame(notes_frame)
        ttk.Label(self.date_inputs_frame, text="从").pack(side=tk.LEFT)
        self.notes_start_entry = ttk.Entry(self.date_inputs_frame, width=15, textvariable=self.notes_start_date)
        self.notes_start_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.date_inputs_frame, text="至").pack(side=tk.LEFT)
        self.notes_end_entry = ttk.Entry(self.date_inputs_frame, width=15, textvariable=self.notes_end_date)
        self.notes_end_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.date_inputs_frame, text="(YYYY-MM-DD)", font=('Microsoft YaHei', 8), foreground='gray').pack(side=tk.LEFT, padx=5)

        # 2. 粉丝数据选项
        followers_frame = ttk.LabelFrame(self.export_config_frame, text="粉丝数据", padding="10")
        followers_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        followers_frame.columnconfigure(0, weight=1)

        ttk.Checkbutton(
            followers_frame,
            text="导出粉丝数据",
            variable=self.export_followers
        ).pack(anchor=tk.W, pady=(0, 10))

        days_frame = ttk.Frame(followers_frame)
        days_frame.pack(fill=tk.X, padx=(20, 0))

        ttk.Label(days_frame, text="最近").pack(side=tk.LEFT)

        # 使用下拉框替代Spinbox
        followers_combo = ttk.Combobox(
            days_frame,
            textvariable=self.followers_days,
            values=["7", "30"],
            width=8,
            font=('Microsoft YaHei', 10),
            state="readonly"  # 禁止自由输入
        )
        followers_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(days_frame, text="天的数据").pack(side=tk.LEFT)

        # 3. 导出按钮
        button_frame = ttk.Frame(self.export_config_frame)
        button_frame.grid(row=2, column=0, pady=10)

        self.export_button = ttk.Button(
            button_frame,
            text="开始导出数据",
            command=self._start_export,
            width=25
        )
        self.export_button.pack()

        # 进度条
        self.export_progress = ttk.Progressbar(
            self.export_config_frame,
            mode='determinate',
            length=400
        )
        self.export_progress.grid(row=3, column=0, pady=10, sticky="ew")

        # 状态显示
        self.export_status_label = ttk.Label(
            self.export_config_frame,
            text="",
            font=('Microsoft YaHei', 9)
        )
        self.export_status_label.grid(row=4, column=0)

    def _create_log_area(self):
        """创建日志区域"""
        log_frame = ttk.LabelFrame(self.main_frame, text="运行日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

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
        status_bar = ttk.Frame(self.main_frame)
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
            text="v2.0",
            relief=tk.SUNKEN
        )
        version_label.pack(side=tk.RIGHT)

    def _toggle_browser(self):
        """切换浏览器显示/隐藏"""
        # TODO: 实现浏览器窗口的显示/隐藏
        self.browser_visible = not self.browser_visible
        if self.browser_visible:
            self.toggle_browser_btn.config(text="隐藏")
        else:
            self.toggle_browser_btn.config(text="显示")

    def _on_export_notes_toggle(self):
        """笔记数据复选框切换"""
        if not self.export_notes.get():
            # 禁用日期选项
            self.notes_start_entry.config(state=tk.DISABLED)
            self.notes_end_entry.config(state=tk.DISABLED)
        else:
            # 恢复日期选项状态
            if self.notes_date_range.get() == "custom":
                self.notes_start_entry.config(state=tk.NORMAL)
                self.notes_end_entry.config(state=tk.NORMAL)

    def _toggle_date_inputs(self):
        """切换日期输入框状态"""
        if self.notes_date_range.get() == "custom":
            self.notes_start_entry.config(state=tk.NORMAL)
            self.notes_end_entry.config(state=tk.NORMAL)
        else:
            self.notes_start_entry.config(state=tk.DISABLED)
            self.notes_end_entry.config(state=tk.DISABLED)

    def _start_export(self):
        """开始导出数据"""
        # 检查是否勾选了任何选项
        if not self.export_notes.get() and not self.export_followers.get():
            messagebox.showwarning("未选择数据", "请至少勾选一项要导出的数据")
            return

        # 收集导出配置
        export_config = {
            'export_notes': self.export_notes.get(),
            'notes_date_range': self.notes_date_range.get(),
            'notes_start_date': self.notes_start_date.get().strip() or None,
            'notes_end_date': self.notes_end_date.get().strip() or None,
            'export_followers': self.export_followers.get(),
            'followers_days': int(self.followers_days.get())  # 转换为整数
        }

        logger.info(f"导出配置: {export_config}")

        # 禁用按钮
        self.export_button.config(state=tk.DISABLED)
        self.export_progress['value'] = 0

        # 启动异步任务
        self._run_async(
            self._do_export(export_config)
        )

    async def _do_export(self, export_config: Dict[str, Any]):
        """执行导出"""
        try:
            def update_progress(msg: str, progress: int):
                """更新进度"""
                self.root.after(0, lambda: self._update_export_progress(msg, progress))

            output_path = await self.unified_exporter.export_all(
                export_config=export_config,
                progress_callback=update_progress
            )

            self.root.after(0, lambda: self._on_export_complete(output_path, None))

        except Exception as e:
            error = e
            self.root.after(0, lambda: self._on_export_complete(None, error))

    def _update_export_progress(self, message: str, progress: int):
        """更新导出进度"""
        self.export_progress['value'] = progress
        self.export_status_label.config(text=message)
        self.root.update_idletasks()

    def _on_export_complete(self, output_path: Optional[str], error: Optional[Exception]):
        """导出完成回调"""
        self.export_button.config(state=tk.NORMAL)

        if error:
            messagebox.showerror("导出失败", f"导出数据失败：\n{str(error)}")
            self.export_status_label.config(text="导出失败")
        else:
            messagebox.showinfo("导出成功", f"数据已导出到：\n{output_path}")
            self.export_status_label.config(text="导出成功")
            self.export_progress['value'] = 100

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
            await page.wait_for_load_state('domcontentloaded')
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

            # 显示导出配置区域
            self.export_config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

            # 隐藏登录按钮
            self.login_button.pack_forget()

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


if __name__ == '__main__':
    app = MainWindowV2()
    app.run()
