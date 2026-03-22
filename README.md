# SecretBox

Developer Password & Secret Vault - 开发者密钥保险箱

## 功能特性

- **AES-256-GCM 加密** - 主密码通过 PBKDF2 派生密钥，所有敏感数据加密存储
- **分类管理** - 预设 OpenAI / Claude / Gemini / DeepSeek 等大模型分类，支持自定义
- **搜索功能** - 按名称、关键词快速搜索密钥
- **一键复制** - Web 和 CLI 均支持快速复制密钥值
- **RESTful API** - JWT 认证的完整 API，支持第三方集成
- **Vue 前端** - Vue 3 + Tailwind CSS 深色科技风格，移动端适配
- **CLI 工具** - 命令行管理密钥 (add/get/list/delete/search/export/import)
- **Telegram Bot** - 通过 Telegram 查询和管理密钥
- **浏览器密码导入** - 支持 Google Chrome / Microsoft Edge 密码 CSV 导入导出
- **Docker 部署** - 多阶段构建，Docker Compose 一键启动
- **GitHub Actions** - 自动构建并推送 Docker 镜像到 GHCR

## 快速开始

### Docker 部署 (推荐)

```bash
docker-compose up --build
```

访问 http://localhost 即可使用。

### 本地开发

**后端：**

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

**前端：**

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器运行在 http://localhost:5173，自动代理 API 到后端 9000 端口。

### CLI 使用

```bash
# 设置主密码
python cli/cli.py setup

# 登录
python cli/cli.py login

# 添加密钥
python cli/cli.py add -c 1

# 列出密钥
python cli/cli.py list
python cli/cli.py list -k "OpenAI"

# 查看密钥
python cli/cli.py get 1

# 搜索
python cli/cli.py search "gemini"

# 导出
python cli/cli.py export -f json -o backup.json

# 导入 Chrome 密码
python cli/cli.py import chrome_passwords.csv -c "通用密码"
```

### Telegram Bot

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_ALLOWED_USERS="123456789,987654321"
python bot/telegram_bot.py
```

Bot 命令: `/login`, `/list`, `/get`, `/add`, `/del`, `/cat`

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/auth/status` | 检查是否已设置主密码 |
| POST | `/api/auth/setup` | 设置主密码 |
| POST | `/api/auth/login` | 登录获取 JWT |
| POST | `/api/auth/change-password` | 修改主密码 |
| GET | `/api/secrets` | 密钥列表 (支持 ?category_id=&keyword=) |
| POST | `/api/secrets` | 创建密钥 |
| GET | `/api/secrets/item/{id}` | 获取密钥详情 |
| PUT | `/api/secrets/{id}` | 更新密钥 |
| DELETE | `/api/secrets/{id}` | 删除密钥 |
| GET | `/api/secrets/q/{keyword}` | 搜索密钥 |
| GET | `/api/categories` | 分类列表 |
| POST | `/api/categories` | 创建分类 |
| DELETE | `/api/categories/{id}` | 删除分类 |
| GET | `/api/export/csv` | 导出 CSV |
| GET | `/api/export/json` | 导出 JSON |
| POST | `/api/import/csv-password` | 导入 CSV |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MASTER_PASSWORD` | changeme | 初始主密码 |
| `JWT_SECRET` | secretbox-jwt-secret-change-me | JWT 签名密钥 |
| `JWT_EXPIRE_MINUTES` | 1440 | JWT 过期时间 (分钟) |
| `DATABASE_URL` | sqlite+aiosqlite:///./data/secretbox.db | 数据库连接 |
| `TELEGRAM_BOT_TOKEN` | - | Telegram Bot Token |
| `TELEGRAM_ALLOWED_USERS` | - | 允许使用的 Telegram 用户 ID |

## Secret 数据模型

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 密钥名称 (明文，可搜索) |
| value | string | 密钥值 (AES-256-GCM 加密) |
| category_id | int | 分类 ID |
| url | string | 关联 URL |
| remark | string | 明文备注/标记 |
| notes | string | 加密备注 (敏感信息) |

## 技术栈

- **后端**: Python 3.11 + FastAPI + SQLAlchemy 2.0
- **数据库**: SQLite (默认) / MySQL (可选)
- **加密**: AES-256-GCM + PBKDF2-HMAC-SHA256
- **前端**: Vue 3 + Vite + Tailwind CSS + Pinia
- **部署**: Docker + Nginx + GitHub Actions

## License

MIT
