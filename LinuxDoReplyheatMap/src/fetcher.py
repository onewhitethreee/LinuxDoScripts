import time
import logging
from datetime import datetime, timedelta

class UserActionFetcher:
    def __init__(self, page, username, base_url, filter_type=5, page_size=30, logger=None):
        self.page = page
        self.username = username
        self.base_url = base_url
        self.filter_type = filter_type
        self.page_size = page_size
        self.logger = logger or logging.getLogger(__name__)

    def get_page_status_js(self):
        try:
            js_code = """
            return fetch(window.location.href, {method: 'HEAD'})
                .then(response => response.status)
                .catch(error => null);
            """
            status_code = self.page.run_js_loaded(js_code)
            return status_code if status_code else None
        except Exception as e:
            self.logger.error(f"获取状态码失败: {e}")
            return None

    def fetch_and_save(self, three_months_ago, output_file, parse_timestamp_func):
        offset = 0
        total_count = 0
        with open(output_file, 'w', encoding='utf-8') as f:
            while True:
                url = f"{self.base_url}?offset={offset}&username={self.username}&filter={self.filter_type}"
                self.logger.info(f"正在请求: offset={offset}")
                try:
                    self.page.get(url)
                    status_code = self.get_page_status_js()
                    if status_code == 403:
                        if hasattr(self.page, 'cf_bypass'):
                            self.page.cf_bypass(self.get_page_status_js)
                        time.sleep(3)
                    time.sleep(1)
                    data = self.page.json
                    if not data or "user_actions" not in data:
                        break
                    current_actions = data["user_actions"]
                    current_count = len(current_actions)
                    if current_count == 0:
                        break
                    self.logger.info(f"获取到 {current_count} 条数据")
                    has_old_data = False
                    for item in current_actions:
                        try:
                            created_at = item['created_at']
                            item_time = parse_timestamp_func(created_at)
                            if item_time >= three_months_ago:
                                f.write(created_at + '\n')
                                f.flush()
                                total_count += 1
                                self.logger.info(f"  ✓ {created_at}")
                            else:
                                self.logger.info(f"  ✗ {created_at} (超出范围)")
                                has_old_data = True
                        except KeyError:
                            self.logger.info("  ? 缺少 created_at 字段")
                            continue
                    if has_old_data:
                        self.logger.info("已获取完三个月内的所有数据")
                        break
                    if current_count < self.page_size:
                        break
                    offset += self.page_size
                except Exception as e:
                    self.logger.error(f"请求出错: {e}")
                    break
        self.logger.info(f"总共获取并保存了 {total_count} 个时间戳到 {output_file}") 
    
    def close(self):
        self.page.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()