import os
from datetime import datetime

MASTER_PASSWORD = os.getenv('MASTER_PASSWORD', 'changeme')
SESSION_SECRET = os.getenv('SESSION_SECRET', 'secretbox')
API_TOKEN_HEADER = 'X-SECRETBOX-TOKEN'
JWT_SECRET = os.getenv('JWT_SECRET', SESSION_SECRET)
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES', '1440'))
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./data/secretbox.db')
DATA_DIR = os.getenv('DATA_DIR', './data')
KDF_ITERATIONS = int(os.getenv('KDF_ITERATIONS', '100000'))
