import os
from typing import Optional

# ============ 数据库配置 ============
# 支持 SQLite 和 MySQL
# SQLite: sqlite+aiosqlite:///./data/secretbox.db
# MySQL: mysql+aiomysql://user:password@host:3306/secretbox
DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()  # sqlite 或 mysql

# MySQL 配置
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_USER = os.getenv('MYSQL_USER', 'secretbox')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'secretbox')

# SQLite 配置
SQLITE_PATH = os.getenv('SQLITE_PATH', './data/secretbox.db')

def get_database_url() -> str:
    """根据配置生成数据库连接 URL"""
    if DB_TYPE == 'mysql':
        return f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    else:
        # 默认使用 SQLite，确保路径以 ./data/ 开头用于 Docker 挂载
        path = SQLITE_PATH
        if not path.startswith('./') and not path.startswith('/'):
            path = f'./data/{path}'
        if not path.endswith('.db'):
            path = f'{path}.db'
        return f"sqlite+aiosqlite:///{path}"

# 保留向后兼容的 DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL', get_database_url())

# 数据目录 (用于 SQLite 和上传文件)
DATA_DIR = os.getenv('DATA_DIR', './data')

# ============ 安全配置 ============
MASTER_PASSWORD = os.getenv('MASTER_PASSWORD', 'changeme')
SESSION_SECRET = os.getenv('SESSION_SECRET', 'secretbox')
API_TOKEN_HEADER = 'X-SECRETBOX-TOKEN'
JWT_SECRET = os.getenv('JWT_SECRET', SESSION_SECRET)
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES', '1440'))

# KDF 迭代次数
KDF_ITERATIONS = int(os.getenv('KDF_ITERATIONS', '100000'))

# ============ 应用配置 ============
SECRETBOX_VERSION = '1.0.0'
