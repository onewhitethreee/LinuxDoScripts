"""
@author: onewhite
@date: 2025-06-14
@description: 根据linux.do的回复数据，生成最近热力图
@usage: python linuxDoUserHeatMap.py
"""
from venv import logger
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import calendar
from collections import Counter
import plotly.graph_objects as go
import plotly.io as pio
from matplotlib.patches import FancyBboxPatch

import re

class HeatmapGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.username = self.extract_username_from_filename(filename)
        self.timestamps = self.load_timestamps_from_file(filename)

    @staticmethod
    def extract_username_from_filename(filename):
        m = re.match(r'timestamps_(.+)\.txt', filename)
        if m:
            return m.group(1)
        return None

    @staticmethod
    def load_timestamps_from_file(filename):
        timestamps = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    timestamp = line.strip()
                    if timestamp:
                        timestamps.append(timestamp)
        except FileNotFoundError:
            logger.error(f"文件 {filename} 不存在")
        except Exception as e:
            logger.error(f"读取文件时出错: {e}")
        return timestamps

    def create_github_heatmap(self, title=None, save_path=None):
        if not self.timestamps:
            logger.error("没有有效的时间戳数据")
            return False
        dates = []
        for ts in self.timestamps:
            try:
                dt = pd.to_datetime(ts)
                dates.append(dt.date())
            except:
                continue
        if not dates:
            logger.error("没有有效的时间戳数据")
            return False
        today = datetime.now().date()
        one_year_ago = today - timedelta(days=365)
        filtered_dates = [d for d in dates if one_year_ago <= d <= today]
        if not filtered_dates:
            logger.error(f"在{one_year_ago}到{today}区间没有找到数据")
            return False
        date_counts = Counter(filtered_dates)
        if not title:
            title = f"{self.username} Reply data heatmap" if self.username else "Reply data heatmap"

        self.create_heatmap(date_counts, one_year_ago, today, title, save_path=save_path)
        return True

    @staticmethod
    def create_heatmap(date_counts, start_date, end_date, title, save_path=None):
        fig, ax = plt.subplots(figsize=(15, 4))
        # 1. 使用更细腻的渐变色
        from matplotlib import cm
        from matplotlib.colors import Normalize
        cmap = matplotlib.colormaps['Greens']
        max_count = max(date_counts.values()) if date_counts else 1
        norm = Normalize(vmin=0, vmax=max_count)
        first_day_weekday = (start_date.weekday() + 1) % 7
        current_date = start_date
        week = 0
        box_size = 0.85
        box_gap = 0.15
        # 记录每个月的起始week
        month_start_weeks = {}
        while current_date <= end_date:
            day_of_week = (current_date.weekday() + 1) % 7
            count = date_counts.get(current_date, 0)
            # 1. 细腻渐变色
            color = cmap(norm(count))
            # 3. 圆角和阴影
            rect = FancyBboxPatch((week + box_gap/2, 6-day_of_week + box_gap/2), box_size, box_size,
                                  boxstyle="round,pad=0.08,rounding_size=0.22",
                                  facecolor=color, edgecolor='white', linewidth=1,
                                  mutation_aspect=1,
                                  alpha=1,
                                  zorder=2)
            # 阴影
            shadow = FancyBboxPatch((week + box_gap/2 + 0.05, 6-day_of_week + box_gap/2 - 0.05), box_size, box_size,
                                    boxstyle="round,pad=0.08,rounding_size=0.22",
                                    facecolor='gray', edgecolor='none', linewidth=0,
                                    alpha=0.15, zorder=1)
            ax.add_patch(shadow)
            ax.add_patch(rect)
            # 4. 记录每个月的起始week
            if current_date.day == 1:
                month_start_weeks[current_date.strftime('%Y-%m')] = week
            current_date += timedelta(days=1)
            if day_of_week == 6:
                week += 1
        # 4. 添加月份分割线
        for month, w in month_start_weeks.items():
            ax.axvline(x=w-0.5, color='#cccccc', linestyle='--', linewidth=1, zorder=0, alpha=0.5)
        # 添加月份标签
        month_positions = []
        current_date = start_date
        current_month = start_date.month
        week = 0
        while current_date <= end_date:
            if current_date.month != current_month:
                month_positions.append((week, calendar.month_abbr[current_month]))
                current_month = current_date.month
            day_of_week = (current_date.weekday() + 1) % 7
            current_date += timedelta(days=1)
            if day_of_week == 6:
                week += 1
        month_positions.append((week, calendar.month_abbr[current_month]))
        for pos, month_name in month_positions:
            ax.text(pos, 7.5, month_name, ha='left', va='bottom', fontsize=9)
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        for i, day in enumerate(days):
            if i % 2 == 1:
                ax.text(-1, 6-i, day, ha='right', va='center', fontsize=8)
        ax.set_xlim(-2, week + 1)
        ax.set_ylim(-0.5, 8)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'{title} - {start_date} 至 {end_date}', fontsize=16, pad=24, fontweight='bold')
        # 图例居中
        heatmap_width = week + 1
        legend_y = -1.2
        legend_x_start = heatmap_width // 2 - 2
        # 1. 图例渐变色
        for i in range(6):
            val = max_count * i / 5
            color = cmap(norm(val))
            rect = FancyBboxPatch((legend_x_start + i, legend_y), box_size, box_size,
                                  boxstyle="round,pad=0.08,rounding_size=0.18",
                                  facecolor=color, edgecolor='white', linewidth=1)
            ax.add_patch(rect)
        ax.text(legend_x_start - 1, legend_y + 0.2, 'Less activity', ha='right', va='center', fontsize=9)
        ax.text(legend_x_start + 6 + 0.5, legend_y + 0.2, 'More activity', ha='left', va='center', fontsize=9)
        plt.tight_layout()
        if save_path:
            # 保存 PNG
            plt.savefig(save_path, dpi=180, bbox_inches='tight')
            

def get_color(count, max_count):
    # GitHub 风格颜色
    colors = ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39']
    if max_count == 0:
        return colors[0]
    if count == 0:
        return colors[0]
    elif count <= max_count * 0.25:
        return colors[1]
    elif count <= max_count * 0.5:
        return colors[2]
    elif count <= max_count * 0.75:
        return colors[3]
    else:
        return colors[4]

# 使用示例
if __name__ == "__main__":
    filename = 'timestamps_onewhite.txt'
    generator = HeatmapGenerator(filename)
    generator.create_github_heatmap(save_path="heatmap_card.png")