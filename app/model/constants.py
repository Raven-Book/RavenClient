"""
Constants 常量
本文件定义了 Raven Client 中的全局常量
"""
from pathlib import Path

HOME = Path.home()
""" HOME 目录 """
CURRENT_DIR = Path(__file__).resolve().parent
""" Raven Client 所在文件夹 """
USER_CONFIG = HOME / ".config"
""" 默认用户配置存放文件夹 """
SAVE_DATA_DIR = USER_CONFIG / 'raven-client'
""" Raven Client 的数据文件夹 """
CONFIG_FILE = SAVE_DATA_DIR / 'config.toml'
""" Raven Client 的配置目录 """


DB_PATH = {
    "sqlite": f"sqlite+aiosqlite:///{SAVE_DATA_DIR}/raven.db"
}
""" Raven Client SQLite 数据库路径 """


REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Host": "httpbin.org",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": "\"Not.A/Brand\";v=\"99\", \"Chromium\";v=\"136\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Linux\"",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-Gpc": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "X-Amzn-Trace-Id": "Root=1-68219cae-0a53211530686acc2c8c1646"
}
""" 请求头 """
