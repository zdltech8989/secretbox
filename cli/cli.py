"""SecretBox CLI - 命令行密钥管理工具"""
import argparse
import sys
import os
import json
import getpass
import httpx

BASE_URL = os.getenv('SECRETBOX_URL', 'http://localhost:9000')
TOKEN_FILE = os.path.join(os.path.expanduser('~'), '.secretbox_token')


def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return f.read().strip()
    return ''


def save_token(token):
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)


def api(method, path, data=None, params=None):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        r = client.request(method, path, json=data, params=params, headers=headers)
    if r.status_code == 401:
        print('Error: 认证失败，请重新登录')
        sys.exit(1)
    if r.status_code >= 400:
        print(f'Error: {r.json().get("detail", r.text)}')
        sys.exit(1)
    return r.json()


def cmd_login(args):
    password = getpass.getpass('主密码: ')
    r = api('POST', '/api/auth/login', {'password': password})
    save_token(r['token'])
    print('登录成功')


def cmd_setup(args):
    password = getpass.getpass('设置主密码 (至少8位): ')
    confirm = getpass.getpass('确认密码: ')
    if password != confirm:
        print('Error: 两次密码不一致')
        sys.exit(1)
    r = api('POST', '/api/auth/setup', {'password': password})
    save_token(r['token'])
    print('主密码设置成功')


def cmd_add(args):
    name = input('密钥名称: ')
    value = getpass.getpass('密钥值: ')
    notes = input('备注 (可选, 回车跳过): ') or None
    url = input('URL (可选, 回车跳过): ') or None
    remark = input('标记 (可选, 回车跳过): ') or None
    category_id = args.category_id
    data = {'name': name, 'value': value}
    if notes:
        data['notes'] = notes
    if url:
        data['url'] = url
    if remark:
        data['remark'] = remark
    if category_id:
        data['category_id'] = category_id
    r = api('POST', '/api/secrets', data)
    print(f'密钥已创建: {r["name"]} (ID: {r["id"]})')


def cmd_get(args):
    r = api('GET', f'/api/secrets/item/{args.id}')
    print(f'名称: {r["name"]}')
    print(f'值: {r["value"]}')
    if r.get('url'):
        print(f'URL: {r["url"]}')
    if r.get('remark'):
        print(f'标记: {r["remark"]}')
    if r.get('notes'):
        print(f'备注: {r["notes"]}')
    print(f'创建: {r["created_at"]}')


def cmd_list(args):
    params = {}
    if args.category:
        params['category_id'] = args.category
    if args.keyword:
        params['keyword'] = args.keyword
    secrets = api('GET', '/api/secrets', params=params)
    if not secrets:
        print('暂无密钥')
        return
    for s in secrets:
        remark = f' [{s["remark"]}]' if s.get('remark') else ''
        print(f'  [{s["id"]}] {s["name"]}{remark}')


def cmd_delete(args):
    if not input(f'确认删除密钥 ID={args.id}? (y/N): ').lower() == 'y':
        print('已取消')
        return
    api('DELETE', f'/api/secrets/{args.id}')
    print('已删除')


def cmd_search(args):
    secrets = api('GET', f'/api/secrets/q/{args.keyword}')
    if not secrets:
        print(f'未找到匹配 "{args.keyword}" 的密钥')
        return
    for s in secrets:
        print(f'  [{s["id"]}] {s["name"]}')


def cmd_categories(args):
    cats = api('GET', '/api/categories')
    for c in cats:
        print(f'  [{c["id"]}] {c["name"]} ({c["secret_count"]} 条)')


def cmd_export(args):
    fmt = args.format or 'json'
    ext = fmt
    if fmt == 'csv':
        url = '/api/export/csv'
        ext = 'csv'
    else:
        url = '/api/export/json'
        ext = 'json'
    filename = args.output or f'secretbox_export.{ext}'
    token = get_token()
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        r = client.get(url, headers={'Authorization': f'Bearer {token}'})
    if r.status_code == 200:
        with open(filename, 'w') as f:
            f.write(r.text)
        print(f'已导出到 {filename}')
    else:
        print(f'导出失败: {r.text}')


def cmd_import(args):
    if not os.path.exists(args.file):
        print(f'文件不存在: {args.file}')
        sys.exit(1)
    with open(args.file, 'r') as f:
        content = f.read()
    token = get_token()
    with httpx.Client(base_url=BASE_URL, timeout=60) as client:
        r = client.post(
            f'/api/import/csv-password?master_password=&category_name={args.category or "通用密码"}',
            files={'file': (args.file, content)},
            headers={'Authorization': f'Bearer {token}'},
        )
    if r.status_code == 200:
        print(f'导入成功: {r.json().get("message", "")}')
    else:
        print(f'导入失败: {r.text}')


def main():
    parser = argparse.ArgumentParser(description='SecretBox CLI - 密钥管理命令行工具')
    sub = parser.add_subparsers(dest='command', help='可用命令')

    sub.add_parser('login', help='登录')
    sub.add_parser('setup', help='首次设置主密码')

    p = sub.add_parser('add', help='添加密钥')
    p.add_argument('-c', '--category-id', type=int, default=None, help='分类ID')

    p = sub.add_parser('get', help='查看密钥')
    p.add_argument('id', type=int, help='密钥ID')

    p = sub.add_parser('list', help='列出密钥')
    p.add_argument('-c', '--category', type=int, default=None, help='按分类筛选')
    p.add_argument('-k', '--keyword', type=str, default=None, help='按关键词搜索')

    p = sub.add_parser('delete', help='删除密钥')
    p.add_argument('id', type=int, help='密钥ID')

    p = sub.add_parser('search', help='搜索密钥')
    p.add_argument('keyword', type=str, help='搜索关键词')

    sub.add_parser('categories', help='列出分类')

    p = sub.add_parser('export', help='导出数据')
    p.add_argument('-f', '--format', choices=['csv', 'json'], default='json')
    p.add_argument('-o', '--output', type=str, default=None, help='输出文件名')

    p = sub.add_parser('import', help='导入CSV')
    p.add_argument('file', type=str, help='CSV文件路径')
    p.add_argument('-c', '--category', type=str, default='通用密码', help='导入分类')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmd_map = {
        'login': cmd_login, 'setup': cmd_setup,
        'add': cmd_add, 'get': cmd_get, 'list': cmd_list,
        'delete': cmd_delete, 'search': cmd_search,
        'categories': cmd_categories, 'export': cmd_export,
        'import': cmd_import,
    }
    cmd_map[args.command](args)


if __name__ == '__main__':
    main()
