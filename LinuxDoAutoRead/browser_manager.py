"""
浏览器管理器模块
负责管理浏览器实例、标签页和登录逻辑
"""

from DrissionPage import Chromium, ChromiumOptions
import time
import config


class BrowserManager:
    """管理浏览器实例和多个标签页"""

    def __init__(self):
        """初始化浏览器管理器"""
        self.browser = None
        self.tabs = []
        self.main_tab = None

    def initialize(self):
        """初始化浏览器并创建标签页"""
        print("正在初始化浏览器...")
        co = ChromiumOptions()
        co.auto_port()
        self.browser = Chromium(co)
        self.main_tab = self.browser.latest_tab

        # 创建4个标签页用于并发操作
        print(f"正在创建 {config.NUM_THREADS} 个标签页...")
        self.tabs = [self.main_tab]
        for i in range(config.NUM_THREADS - 1):
            new_tab = self.browser.new_tab()
            self.tabs.append(new_tab)

        print(f"✓ 已创建 {len(self.tabs)} 个标签页")

    def login(self):
        """登录到论坛(只需登录一次,所有标签页共享session)"""
        print("正在登录论坛...")
        tab = self.main_tab
        tab.get(config.LOGIN_URL)
        time.sleep(2)

        try:
            # 输入用户名和密码
            account_name = tab.ele("#login-account-name")
            account_name.input(config.USERNAME)
            password = tab.ele("#login-account-password")
            password.input(config.PASSWORD)
            login_button = tab.ele("#login-button")
            login_button.click()

            # 等待登录完成
            time.sleep(2)
            print(f"✓ 登录成功: {config.USERNAME}")
            return True
        except Exception as e:
            print(f"✗ 登录失败: {e}")
            return False

    def get_unread_posts(self):
        """获取未读帖子列表"""
        try:
            tab = self.main_tab
            tab.get(config.UNSEEN_URL)
            time.sleep(config.PAGE_LOAD_DELAY)

            # 查找所有未读帖子
            unread_posts = tab.eles("css:.topic-list tbody tr")
            unread_links = []

            for post in unread_posts:
                try:
                    # 获取帖子标题链接
                    link = post.ele("css:a.title", timeout=1)
                    if link:
                        post_url = link.attr("href")
                        if not post_url.startswith("http"):
                            post_url = config.FORUM_URL + post_url
                        post_title = link.text

                        # 尝试提取帖子ID
                        post_id = None
                        if "/t/" in post_url:
                            parts = post_url.split("/t/")
                            if len(parts) > 1:
                                id_part = (
                                    parts[1].split("/")[1] if "/" in parts[1] else None
                                )
                                if id_part and id_part.isdigit():
                                    post_id = id_part

                        unread_links.append(
                            {"url": post_url, "title": post_title, "id": post_id}
                        )
                except:
                    continue

            return unread_links
        except Exception as e:
            print(f"获取未读帖子时出错: {e}")
            return []

    def get_tab(self, index):
        """获取指定索引的标签页"""
        if 0 <= index < len(self.tabs):
            return self.tabs[index]
        return None

    def close(self):
        """关闭浏览器"""
        if self.browser:
            print("正在关闭浏览器...")
            # 浏览器会自动关闭,不需要显式调用
