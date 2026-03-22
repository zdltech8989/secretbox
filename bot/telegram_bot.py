"""SecretBox Telegram Bot - 通过 Telegram 查询和管理密钥"""
import os
import sys
import asyncio
import httpx

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

API_URL = os.getenv('SECRETBOX_URL', 'http://localhost:9000')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
ALLOWED_USERS = set(int(u) for u in os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',') if u.strip())

_tokens: dict[int, str] = {}


def get_token(user_id: int) -> str:
    return _tokens.get(user_id, '')


def set_token(user_id: int, token: str):
    _tokens[user_id] = token


async def api_call(method: str, path: str, user_id: int, json_data=None):
    token = get_token(user_id)
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    async with httpx.AsyncClient(base_url=API_URL, timeout=15) as client:
        r = await client.request(method, path, json=json_data, headers=headers)
    if r.status_code == 401:
        return None
    return r.json() if r.status_code < 400 else None


def auth_check(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if ALLOWED_USERS and uid not in ALLOWED_USERS:
            await update.message.reply_text('⛔ 未授权用户')
            return
        if not get_token(uid):
            await update.message.reply_text('🔒 请先使用 /login <主密码> 登录')
            return
        return await func(update, context)
    return wrapper


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🔐 SecretBox Bot\n\n'
        '/login <密码> - 登录\n'
        '/list - 列出所有密钥\n'
        '/get <名称> - 搜索密钥\n'
        '/cat - 列出分类\n'
        '/help - 帮助'
    )


async def login_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('用法: /login <主密码>')
        return
    password = ' '.join(context.args)
    async with httpx.AsyncClient(base_url=API_URL, timeout=15) as client:
        r = await client.post('/api/auth/login', json={'password': password})
    if r.status_code == 200:
        data = r.json()
        set_token(update.effective_user.id, data['token'])
        await update.message.reply_text('✅ 登录成功')
    else:
        await update.message.reply_text('❌ 密码错误')


@auth_check
async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    keyword = ' '.join(context.args) if context.args else None
    if keyword:
        data = await api_call('GET', f'/api/secrets/q/{keyword}', uid)
    else:
        data = await api_call('GET', '/api/secrets', uid)
    if not data:
        await update.message.reply_text('暂无密钥或请求失败')
        return
    if not isinstance(data, list):
        await update.message.reply_text('请求失败，请重新登录')
        set_token(uid, '')
        return
    if not data:
        await update.message.reply_text('未找到匹配的密钥')
        return
    lines = [f'📋 共 {len(data)} 条:\n']
    for s in data[:20]:
        name = s['name']
        remark = f' ({s["remark"]})' if s.get('remark') else ''
        lines.append(f'  [{s["id"]}] {name}{remark}')
    text = '\n'.join(lines)
    if len(data) > 20:
        text += f'\n...还有 {len(data) - 20} 条'
    await update.message.reply_text(text)


@auth_check
async def get_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not context.args:
        await update.message.reply_text('用法: /get <密钥ID>')
        return
    try:
        sid = int(context.args[0])
    except ValueError:
        await update.message.reply_text('请输入有效的密钥ID')
        return
    data = await api_call('GET', f'/api/secrets/item/{sid}', uid)
    if not data or 'error' in data:
        await update.message.reply_text('获取失败，请检查ID')
        return
    lines = [
        f'🔑 {data["name"]}',
        f'值: `{data["value"]}`',
    ]
    if data.get('url'):
        lines.append(f'URL: {data["url"]}')
    if data.get('remark'):
        lines.append(f'标记: {data["remark"]}')
    if data.get('notes'):
        lines.append(f'备注: {data["notes"]}')
    await update.message.reply_text('\n'.join(lines), parse_mode='Markdown')


@auth_check
async def cat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = await api_call('GET', '/api/categories', uid)
    if not data or not isinstance(data, list):
        await update.message.reply_text('获取分类失败')
        return
    lines = ['📂 分类列表:\n']
    for c in data:
        lines.append(f'  [{c["id"]}] {c["name"]} ({c["secret_count"]} 条)')
    await update.message.reply_text('\n'.join(lines))


@auth_check
async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if len(context.args) < 2:
        await update.message.reply_text('用法: /add <名称> <密钥值> [分类ID]')
        return
    name = context.args[0]
    value = context.args[1]
    cat_id = int(context.args[2]) if len(context.args) > 2 else None
    body = {'name': name, 'value': value}
    if cat_id:
        body['category_id'] = cat_id
    data = await api_call('POST', '/api/secrets', uid, body)
    if data and 'id' in data:
        await update.message.reply_text(f'✅ 已添加: {name} (ID: {data["id"]})')
    else:
        await update.message.reply_text('添加失败')


@auth_check
async def del_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not context.args:
        await update.message.reply_text('用法: /del <密钥ID>')
        return
    try:
        sid = int(context.args[0])
    except ValueError:
        await update.message.reply_text('请输入有效的密钥ID')
        return
    data = await api_call('DELETE', f'/api/secrets/{sid}', uid)
    await update.message.reply_text('✅ 已删除' if data else '删除失败')


def main():
    if not BOT_TOKEN:
        print('Error: TELEGRAM_BOT_TOKEN 环境变量未设置')
        sys.exit(1)
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start_cmd))
    app.add_handler(CommandHandler('help', start_cmd))
    app.add_handler(CommandHandler('login', login_cmd))
    app.add_handler(CommandHandler('list', list_cmd))
    app.add_handler(CommandHandler('get', get_cmd))
    app.add_handler(CommandHandler('cat', cat_cmd))
    app.add_handler(CommandHandler('add', add_cmd))
    app.add_handler(CommandHandler('del', del_cmd))

    print('SecretBox Telegram Bot 已启动...')
    app.run_polling()


if __name__ == '__main__':
    main()
