import logging
from datetime import datetime, timedelta
from src.browser import BrowserManager
from src.fetcher import UserActionFetcher
from src.utils import parse_timestamp
from src.linuxDoUserHeatMap import HeatmapGenerator  
import argparse
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="抓取 linux.do 用户活跃数据并生成热力图")
    parser.add_argument("username", nargs="?", default="onewhite", help="要抓取的用户名")
    parser.add_argument("days", nargs="?", type=int, default=90, help="抓取最近多少天的数据（整数，默认90天）")
    args = parser.parse_args()

    load_dotenv()

    base_url = "https://linux.do/user_actions.json"
    username = args.username
    filter_type = 5 
    """
    1 = LIKE (点赞)
    2 = WAS_LIKED (被点赞)
    4 = NEW_TOPIC (新话题)
    5 = REPLY (回复)
    """
    offset = 30
    # browser_path = None
    browser_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" # 此处为启动edge浏览器
    
    proxy_conf = {
        "host": os.getenv("PROXY_HOST"),
        "port": os.getenv("PROXY_PORT"),
        "user": os.getenv("PROXY_USER"),
        "password": os.getenv("PROXY_PASSWORD"),
        "plugin_path": "/tmp/111"
    }
    
    # 如果有任意一项为空，则不启用代理
    if not all([proxy_conf["host"], proxy_conf["port"], proxy_conf["user"], proxy_conf["password"]]):
        logger.info("没有配置代理，不启用代理")
        proxy_conf = None
    
    turnstile_patch_path = "turnstilePatch"  
    x_months_ago = datetime.now() - timedelta(days=args.days)
    
    logger.info(f"获取 {args.username} 的 {x_months_ago.strftime('%Y-%m-%d %H:%M:%S')} 之后的数据")
    output_file = f"timestamps_{username}.txt"

    browser_mgr = BrowserManager(browser_path, proxy_conf, turnstile_patch_path)
    page = browser_mgr.setup_browser()
    # 给 page 动态加 cf_bypass 方法，便于 fetcher 调用
    setattr(page, 'cf_bypass', browser_mgr.cf_bypass)

    fetcher = UserActionFetcher(
        page=page,
        username=username,
        base_url=base_url,
        filter_type=filter_type,
        page_size=offset,
        logger=logger
    )
    fetcher.fetch_and_save(x_months_ago, output_file, parse_timestamp)

    # 数据抓取完成后生成热力图
    logger.info("正在生成热力图...")
    generator = HeatmapGenerator(output_file)
    success = generator.create_github_heatmap(save_path="heatmap_card.png")
    if success:
        logger.info(f"热力图已保存为 heatmap_card.png")