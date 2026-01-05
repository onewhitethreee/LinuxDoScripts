"""
线程协调器模块
负责管理多个工作线程和任务队列
"""

import threading
import queue
import time
from post_reader import PostReader
import config


class ThreadCoordinator:
    """管理工作线程和任务分发"""

    def __init__(self, browser_manager):
        """
        初始化线程协调器

        Args:
            browser_manager: 浏览器管理器实例
        """
        self.browser_manager = browser_manager
        self.task_queue = queue.Queue()
        self.threads = []
        self.stats_lock = threading.Lock()

        # 全局已读帖子追踪(使用URL作为唯一标识)
        self.read_posts = set()
        self.read_posts_lock = threading.Lock()

        # 统计信息
        self.total_read = 0
        self.total_success = 0
        self.total_failed = 0
        self.total_skipped = 0  # 跳过的重复帖子数
        self.is_running = False

    def start(self):
        """启动工作线程"""
        print(f"\n正在启动 {config.NUM_THREADS} 个工作线程...")
        self.is_running = True

        for i in range(config.NUM_THREADS):
            thread = threading.Thread(
                target=self._worker, args=(i,), name=f"Worker-{i}"
            )
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

        print(f"✓ {config.NUM_THREADS} 个工作线程已启动\n")

    def _worker(self, thread_id):
        """
        工作线程函数

        Args:
            thread_id: 线程ID
        """
        # 获取该线程专用的标签页
        tab = self.browser_manager.get_tab(thread_id)

        if not tab:
            print(f"[线程{thread_id}] ✗ 无法获取标签页")
            return

        print(f"[线程{thread_id}] 已启动,等待任务...")

        while self.is_running:
            try:
                # 从队列获取任务,超时1秒
                post_info = self.task_queue.get(timeout=1)

                # 读取帖子
                success = PostReader.read_post(tab, post_info, thread_id)

                # 标记为已读
                with self.read_posts_lock:
                    self.read_posts.add(post_info["url"])

                # 更新统计信息
                with self.stats_lock:
                    self.total_read += 1
                    if success:
                        self.total_success += 1
                    else:
                        self.total_failed += 1

                # 标记任务完成
                self.task_queue.task_done()

                # 添加延迟避免请求过快
                time.sleep(config.POST_READ_DELAY)

            except queue.Empty:
                # 队列为空,继续等待
                continue
            except Exception as e:
                print(f"[线程{thread_id}] 处理任务时出错: {e}")
                self.task_queue.task_done()

    def add_task(self, post_info):
        """
        添加任务到队列(检查是否已读)

        Args:
            post_info: 帖子信息字典

        Returns:
            bool: 是否成功添加(False表示已读过,跳过)
        """
        # 检查是否已读过
        with self.read_posts_lock:
            if post_info["url"] in self.read_posts:
                with self.stats_lock:
                    self.total_skipped += 1
                return False

        self.task_queue.put(post_info)
        return True

    def add_tasks(self, post_list):
        """
        批量添加任务

        Args:
            post_list: 帖子信息列表

        Returns:
            tuple: (添加数量, 跳过数量)
        """
        added = 0
        skipped = 0
        for post_info in post_list:
            if self.add_task(post_info):
                added += 1
            else:
                skipped += 1
        return added, skipped

    def wait_completion(self):
        """等待所有任务完成"""
        self.task_queue.join()

    def stop(self):
        """停止所有工作线程"""
        print("\n正在停止工作线程...")
        self.is_running = False

        # 等待所有线程结束
        for thread in self.threads:
            thread.join(timeout=2)

        print("✓ 所有工作线程已停止")

    def get_stats(self):
        """
        获取统计信息

        Returns:
            dict: 统计信息字典
        """
        with self.stats_lock:
            return {
                "total_read": self.total_read,
                "total_success": self.total_success,
                "total_failed": self.total_failed,
                "total_skipped": self.total_skipped,
                "success_rate": (
                    (self.total_success / self.total_read * 100)
                    if self.total_read > 0
                    else 0
                ),
            }

    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        print("\n" + "=" * 50)
        print("统计信息:")
        print(f"  总共阅读: {stats['total_read']} 个帖子")
        print(f"  成功: {stats['total_success']} 个")
        print(f"  失败: {stats['total_failed']} 个")
        print(f"  跳过(已读): {stats['total_skipped']} 个")
        print(f"  成功率: {stats['success_rate']:.1f}%")
        print("=" * 50)
