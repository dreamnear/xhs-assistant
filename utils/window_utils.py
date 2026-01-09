"""
窗口定位工具
用于移动浏览器窗口到GUI窗口的右侧
"""
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)


def position_browser_window_right(gui_width=400, gui_height=700):
    """
    将浏览器窗口定位到GUI窗口右侧

    Args:
        gui_width: GUI窗口宽度
        gui_height: GUI窗口高度
    """
    try:
        if sys.platform == 'darwin':  # macOS
            _position_browser_macos(gui_width, gui_height)
        elif sys.platform == 'win32':  # Windows
            _position_browser_windows(gui_width, gui_height)
        elif sys.platform.startswith('linux'):
            _position_browser_linux(gui_width, gui_height)
    except Exception as e:
        logger.warning(f"无法定位浏览器窗口: {e}")


def _position_browser_macos(gui_width, gui_height):
    """在 macOS 上定位浏览器窗口"""
    try:
        # 等待浏览器窗口完全显示
        import time
        time.sleep(1)

        # 使用 AppleScript 查找并移动 Chromium 窗口
        # 改进版：尝试多种方式定位窗口
        script = f'''
tell application "System Events"
    set chromeProcess to missing value

    -- 尝试找到 Chromium 或 Chrome 进程
    if exists process "Chromium" then
        set chromeProcess to process "Chromium"
    else if exists process "Google Chrome" then
        set chromeProcess to process "Google Chrome"
    else if exists process "Chrome" then
        set chromeProcess to process "Chrome"
    end if

    if chromeProcess is not missing value then
        try
            tell chromeProcess
            -- 尝试通过窗口属性操作
            set windowCount to count of windows
            if windowCount > 0 then
                set frontWindow to window 1
                set position of frontWindow to {{{gui_width + 20}, 40}}
                set size of frontWindow to {{900, {gui_height}}}
                return "success"
            end if
            end tell
        on error errMsg
            return "error: " & errMsg
        end try
    else
        return "no browser"
    end if
end tell
'''
        result = subprocess.run(['osascript', '-e', script],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0 and "success" in result.stdout:
            logger.info("浏览器窗口已定位到右侧")
        else:
            logger.debug(f"窗口定位脚本结果: {result.stdout}")

    except subprocess.TimeoutExpired:
        logger.warning("定位浏览器窗口超时")
    except Exception as e:
        logger.debug(f"定位浏览器窗口出错: {e}")


def _position_browser_windows(gui_width, gui_height):
    """在 Windows 上定位浏览器窗口"""
    try:
        import win32gui
        import win32con

        def callback(hwnd, extra):
            """枚举窗口回调函数"""
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                # 查找 Chromium 或 Chrome 窗口
                if 'Chromium' in title or 'Chrome' in title:
                    # 移动窗口到GUI右侧
                    win32gui.SetWindowPos(
                        hwnd,
                        win32con.HWND_TOP,
                        gui_width + 20, 40,  # x, y
                        800, gui_height,     # width, height
                        win32con.SWP_SHOWWINDOW
                    )
                    logger.info(f"已移动窗口: {title}")
            return True

        # 枚举所有顶级窗口
        win32gui.EnumWindows(callback, None)
    except ImportError:
        logger.warning("需要安装 pywin32: pip install pywin32")
    except Exception as e:
        logger.warning(f"定位浏览器窗口出错: {e}")


def _position_browser_linux(gui_width, gui_height):
    """在 Linux 上定位浏览器窗口"""
    try:
        # 使用 wmctrl 命令
        subprocess.run([
            'wmctrl', '-r',
            'Chromium',
            '-e',
            f'0,{gui_width + 20},40,800,{gui_height}'
        ], check=True, capture_output=True, timeout=5)
        logger.info("浏览器窗口已定位到右侧")
    except FileNotFoundError:
        logger.warning("需要安装 wmctrl: sudo apt-get install wmctrl")
    except subprocess.CalledProcessError as e:
        logger.warning(f"定位浏览器窗口失败: {e}")
    except Exception as e:
        logger.warning(f"定位浏览器窗口出错: {e}")
