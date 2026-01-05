# linux.do 用户活跃数据热力图

## 项目简介

本项目用于自动抓取 linux.do 某用户近三个月的活跃时间数据，并生成 GitHub 风格的年度热力图。

## 主要功能

- 自动获取某用户的活跃数据（回复）
- 实时保存数据到本地 txt 文件
- 一键生成年度热力图（PNG 图片）

## 依赖环境

- Python 3.8 及以上
- 主要依赖包：
  - DrissionPage
  - matplotlib
  - pandas
  - numpy
  - plotly

安装依赖示例：

```bash
pip install -r requirements.txt
```

如果你为linux用户，可以使用uv管理python环境，示例如下：
```
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## 使用方法

```bash
python main.py 用户名 天数
```

用户名：需要获取热力图的用户名
天数：需要获取最近多少天的数据（整数，默认90天）

---

另外在.env文件中有配置proxy，如果不需要，忽视即可。

在main中还有一个browser_path配置，默认为None，如果需要使用其他浏览器，可以修改为其他浏览器路径。

## 输出说明

- `timestamps_用户名.txt`：抓取到的所有时间戳（每行一个 ISO 格式时间）。
- `heatmap_card.png`：年度活跃热力图，可直接用于展示。

![](https://img.164314.xyz/2025/06/c40deac1a348168f341e934cfcd72a74.png)

## 目录结构

- `main.py`：主流程入口
- `browser.py`：浏览器与代理、验证码处理
- `fetcher.py`：数据抓取与分页
- `utils.py`：通用工具函数
- `linuxDoUserHeatMap.py`：热力图生成
- `turnstilePatch/`：验证码补丁插件
  
----

需要注意的是，热力图的数据是根据timestamps_用户名.txt文件中的数据生成的，热力图的时间范围为一年，timestamps时间范围则是用程序命令行的方式获取的。
