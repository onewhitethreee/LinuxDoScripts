"""
帖子阅读器模块
负责阅读单个帖子的逻辑
"""

import time
import config


class PostReader:
    """处理单个帖子的阅读逻辑"""

    @staticmethod
    def read_post(tab, post_info, thread_id):
        """
        阅读单个帖子

        Args:
            tab: 浏览器标签页对象
            post_info: 帖子信息字典 {url, title, id}
            thread_id: 线程ID(用于日志)

        Returns:
            bool: 是否成功阅读
        """
        try:
            post_url = post_info["url"]
            post_title = post_info["title"]
            post_id = post_info.get("id")

            print(f"[线程{thread_id}] 正在阅读: {post_title}")

            # 导航到帖子页面
            tab.get(post_url)
            time.sleep(config.PAGE_LOAD_DELAY)

            # TODO: 这里可以实现timing API调用
            # 目前使用滚动方案作为备选
            PostReader._scroll_and_read(tab, thread_id)

            print(f"[线程{thread_id}] ✓ 完成阅读: {post_title}")
            return True

        except Exception as e:
            print(f"[线程{thread_id}] ✗ 阅读帖子时出错: {e}")
            return False

    @staticmethod
    def _scroll_and_read(tab, thread_id):
        """
        滚动页面模拟阅读

        Args:
            tab: 浏览器标签页对象
            thread_id: 线程ID(用于日志)
        """
        import time as time_module

        try:
            scroll_pause_time = config.SCROLL_PAUSE_TIME
            max_attempts = config.MAX_SCROLL_ATTEMPTS
            stable_threshold = config.STABLE_COUNT_THRESHOLD

            # 添加总时间限制,防止无限滚动
            max_scroll_time = config.MAX_SCROLL_TIME
            start_time = time_module.time()

            last_height = 0
            stable_count = 0

            print(f"[线程{thread_id}] 开始滚动阅读...")

            # 持续滚动直到高度稳定或超时
            for attempt in range(max_attempts):
                # 检查是否超时
                elapsed = time_module.time() - start_time
                if elapsed > max_scroll_time:
                    print(f"[线程{thread_id}] 滚动超时({elapsed:.1f}秒),停止滚动")
                    break

                try:
                    # 滚动到底部(添加超时保护)
                    tab.run_js("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(scroll_pause_time)

                    # 获取当前页面高度(添加超时保护)
                    current_height = tab.run_js("return document.body.scrollHeight")

                    # 如果获取不到高度,可能页面有问题
                    if current_height is None or current_height == 0:
                        print(f"[线程{thread_id}] 无法获取页面高度,可能页面已崩溃")
                        break

                    if current_height > last_height:
                        last_height = current_height
                        stable_count = 0
                    else:
                        stable_count += 1

                    # 如果高度稳定,说明到底了
                    if stable_count >= stable_threshold:
                        print(f"[线程{thread_id}] 页面高度稳定,滚动完成")
                        break

                except Exception as e:
                    print(f"[线程{thread_id}] 滚动过程中出错: {e}")
                    # 继续尝试,不要因为一次失败就放弃
                    continue

            # 最终验证(减少次数,避免卡住)
            try:
                for _ in range(2):
                    tab.run_js("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.3)
            except:
                pass

            total_time = time_module.time() - start_time
            print(f"[线程{thread_id}] 滚动完成,耗时 {total_time:.1f}秒")

        except Exception as e:
            print(f"[线程{thread_id}] 滚动页面时出错: {e}")

    @staticmethod
    def call_timing_api(tab, post_id, thread_id):
        """
        调用timing API标记帖子为已读

        Args:
            tab: 浏览器标签页对象
            post_id: 帖子ID
            thread_id: 线程ID(用于日志)

        Returns:
            bool: 是否成功调用API
        """
        # TODO: 实现timing API调用
        # 需要用户提供API的详细信息
        # 包括: URL格式、请求方法、参数、请求头等
        print(f"[线程{thread_id}] TODO: 调用timing API for post {post_id}")
        return False
