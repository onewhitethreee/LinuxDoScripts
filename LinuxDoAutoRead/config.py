# Discourse 多线程自动阅读器配置文件

# 论坛配置
FORUM_URL = "https://linux.do"
LOGIN_URL = "https://linux.do/login"
UNSEEN_URL = "https://linux.do/unseen"

# 登录凭据
USERNAME = ""
PASSWORD = ""

# 线程配置
NUM_THREADS = 4  # 并发线程数量

# 滚动配置(如果使用滚动方案)
SCROLL_PAUSE_TIME = 2  # 滚动后等待时间(秒)
SCROLL_STEP = 500  # 每次滚动像素
MAX_SCROLL_ATTEMPTS = 150  # 最大滚动次数
STABLE_COUNT_THRESHOLD = 5  # 高度稳定次数阈值

# 延迟配置
PAGE_LOAD_DELAY = 1  # 页面加载等待时间(秒)
POST_READ_DELAY = 1  # 读完一个帖子后的延迟(秒)

# 超时配置
MAX_SCROLL_TIME = 60  # 单个帖子最大滚动时间(秒)
MAX_POST_READ_TIME = 90  # 单个帖子最大阅读时间(秒)

# 日志配置
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
