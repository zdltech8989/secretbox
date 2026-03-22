-- SecretBox 初始化 SQL
-- 注意：密码使用 PBKDF2-SHA256 哈希，这里是 'a123456' 的哈希值
-- 生产环境请使用 Python 生成真实的密码哈希

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT 0 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建主密钥表
CREATE TABLE IF NOT EXISTS master_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    salt TEXT NOT NULL,
    verify_hash VARCHAR(128) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建分类表
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    icon VARCHAR(50) DEFAULT 'folder',
    sort_order INTEGER DEFAULT 0
);

-- 创建密钥表
CREATE TABLE IF NOT EXISTS secrets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    encrypted_value TEXT NOT NULL,
    nonce TEXT NOT NULL,
    category_id INTEGER,
    encrypted_notes TEXT,
    notes_nonce TEXT,
    url VARCHAR(2048),
    remark VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_secrets_name ON secrets(name);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- 插入管理员账号 (用户名: zhangdl, 密码: a123456)
-- 注意：这是示例哈希，生产环境请使用 Python 的 hash_password() 生成
INSERT OR IGNORE INTO users (username, password_hash, is_admin)
VALUES ('zhangdl', 'pbkdf2:sha256:600000$saltplaceholder$hashplaceholder', 1);

-- 插入默认分类
INSERT OR IGNORE INTO categories (name, icon, sort_order) VALUES
('OpenAI', 'bot', 1),
('Claude', 'brain', 2),
('Gemini', 'sparkles', 3),
('DeepSeek', 'flame', 4),
('通用密码', 'lock', 10),
('API Token', 'key', 11),
('SSH Key', 'terminal', 12),
('数据库', 'database', 13);
