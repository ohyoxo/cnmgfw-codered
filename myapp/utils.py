import os
import re
import shutil
import subprocess
import requests
import json
import time
import base64
import threading
from django.conf import settings

# 生成 xr-ay 配置文件
def generate_config():
    config = {
        "log": {"access": "/dev/null", "error": "/dev/null", "loglevel": "none"},
        "inbounds": [
            {
                "port": settings.ARGO_PORT,
                "protocol": "vless",
                "settings": {
                    "clients": [{"id": settings.UUID, "flow": "xtls-rprx-vision"}],
                    "decryption": "none",
                    "fallbacks": [
                        {"dest": 3001},
                        {"path": "/vless-argo", "dest": 3002},
                        {"path": "/vmess-argo", "dest": 3003},
                        {"path": "/trojan-argo", "dest": 3004},
                    ],
                },
                "streamSettings": {"network": "tcp"},
            },
            {
                "port": 3001,
                "listen": "127.0.0.1",
                "protocol": "vless",
                "settings": {"clients": [{"id": settings.UUID}], "decryption": "none"},
                "streamSettings": {"network": "ws", "security": "none"},
            },
            {
                "port": 3002,
                "listen": "127.0.0.1",
                "protocol": "vless",
                "settings": {"clients": [{"id": settings.UUID, "level": 0}], "decryption": "none"},
                "streamSettings": {"network": "ws", "security": "none", "wsSettings": {"path": "/vless-argo"}},
                "sniffing": {"enabled": True, "destOverride": ["http", "tls", "quic"], "metadataOnly": False},
            },
            {
                "port": 3003,
                "listen": "127.0.0.1",
                "protocol": "vmess",
                "settings": {"clients": [{"id": settings.UUID, "alterId": 0}]},
                "streamSettings": {"network": "ws", "wsSettings": {"path": "/vmess-argo"}},
                "sniffing": {"enabled": True, "destOverride": ["http", "tls", "quic"], "metadataOnly": False},
            },
            {
                "port": 3004,
                "listen": "127.0.0.1",
                "protocol": "trojan",
                "settings": {"clients": [{"password": settings.UUID}]},
                "streamSettings": {"network": "ws", "security": "none", "wsSettings": {"path": "/trojan-argo"}},
                "sniffing": {"enabled": True, "destOverride": ["http", "tls", "quic"], "metadataOnly": False},
            },
        ],
        "dns": {"servers": ["https+local://8.8.8.8/dns-query"]},
        "outbounds": [
            {"protocol": "freedom", "tag": "direct"},
            {"protocol": "blackhole", "tag": "block"},
        ],
    }
    with open(os.path.join(settings.FILE_PATH, 'config.json'), 'w', encoding='utf-8') as config_file:
        json.dump(config, config_file, ensure_ascii=False, indent=2)

# 判断系统架构
def get_system_architecture():
    arch = os.uname().machine
    if 'arm' in arch or 'aarch64' in arch or 'arm64' in arch:
        return 'arm'
    else:
        return 'amd'

# 下载文件
def download_file(file_name, file_url):
    file_path = os.path.join(settings.FILE_PATH, file_name)
    with requests.get(file_url, stream=True) as response, open(file_path, 'wb') as file:
        shutil.copyfileobj(response.raw, file)

# 根据架构获取文件列表
def get_files_for_architecture(architecture):
    if architecture == 'arm':
        return [
            {'file_name': 'npm', 'file_url': 'https://arm64.2go.us.kg/agent'},
            {'file_name': 'web', 'file_url': 'https://arm64.2go.us.kg/web'},
            {'file_name': 'bot', 'file_url': 'https://arm64.2go.us.kg/bot'},
        ]
    elif architecture == 'amd':
        return [
            {'file_name': 'npm', 'file_url': 'https://amd64.2go.us.kg/agent'},
            {'file_name': 'web', 'file_url': 'https://amd64.2go.us.kg/web'},
            {'file_name': 'bot', 'file_url': 'https://amd64.2go.us.kg/2go'},
        ]
    return []

# 授权文件
def authorize_files(file_paths):
    new_permissions = 0o775
    for relative_file_path in file_paths:
        absolute_file_path = os.path.join(settings.FILE_PATH, relative_file_path)
        try:
            os.chmod(absolute_file_path, new_permissions)
            print(f"Empowerment success for {absolute_file_path}: {oct(new_permissions)}")
        except Exception as e:
            print(f"Empowerment failed for {absolute_file_path}: {e}")

# 获取 Cloudflare 参数
def get_cloud_flare_args():
    processed_auth = settings.ARGO_AUTH
    try:
        auth_data = json.loads(settings.ARGO_AUTH)
        if 'TunnelSecret' in auth_data and 'AccountTag' in auth_data and 'TunnelID' in auth_data:
            processed_auth = 'TunnelSecret'
    except json.JSONDecodeError:
        pass

    if not processed_auth and not settings.ARGO_DOMAIN:
        args = f'tunnel --edge-ip-version auto --no-autoupdate --protocol http2 --logfile {settings.FILE_PATH}/boot.log --loglevel info --url http://localhost:{settings.ARGO_PORT}'
    elif processed_auth == 'TunnelSecret':
        args = f'tunnel --edge-ip-version auto --config {settings.FILE_PATH}/tunnel.yml run'
    elif processed_auth and settings.ARGO_DOMAIN and 120 <= len(processed_auth) <= 250:
        args = f'tunnel --edge-ip-version auto --no-autoupdate --protocol http2 run --token {processed_auth}'
    else:
        args = f'tunnel --edge-ip-version auto --no-autoupdate --protocol http2 --logfile {settings.FILE_PATH}/boot.log --loglevel info --url http://localhost:{settings.ARGO_PORT}'
    return args

# 下载并运行文件
def download_files_and_run():
    architecture = get_system_architecture()
    files_to_download = get_files_for_architecture(architecture)

    if not files_to_download:
        print("Can't find a file for the current architecture")
        return

    for file_info in files_to_download:
        try:
            download_file(file_info['file_name'], file_info['file_url'])
            print(f"Downloaded {file_info['file_name']} successfully")
        except Exception as e:
            print(f"Download {file_info['file_name']} failed: {e}")

    files_to_authorize = ['npm', 'web', 'bot']
    authorize_files(files_to_authorize)

    command1 = f"nohup {settings.FILE_PATH}/web -c {settings.FILE_PATH}/config.json >/dev/null 2>&1 &"
    try:
        subprocess.run(command1, shell=True, check=True)
        print('web is running')
        subprocess.run('sleep 1', shell=True)
    except subprocess.CalledProcessError as e:
        print(f'web running error: {e}')

    if os.path.exists(os.path.join(settings.FILE_PATH, 'bot')):
        args = get_cloud_flare_args()
        try:
            subprocess.run(f"nohup {settings.FILE_PATH}/bot {args} >/dev/null 2>&1 &", shell=True, check=True)
            print('bot is running')
            subprocess.run('sleep 2', shell=True)
        except subprocess.CalledProcessError as e:
            print(f'Error executing command: {e}')

    subprocess.run('sleep 3', shell=True)

# 配置 Argo Tunnel
def argo_config():
    if not settings.ARGO_AUTH or not settings.ARGO_DOMAIN:
        print("ARGO_DOMAIN or ARGO_AUTH is empty, use quick Tunnels")
        return

    if 'TunnelSecret' in settings.ARGO_AUTH:
        with open(os.path.join(settings.FILE_PATH, 'tunnel.json'), 'w') as file:
            file.write(settings.ARGO_AUTH)
        tunnel_yaml = f"""
tunnel: {settings.ARGO_AUTH.split('"')[11]}
credentials-file: {os.path.join(settings.FILE_PATH, 'tunnel.json')}
protocol: http2

ingress:
  - hostname: {settings.ARGO_DOMAIN}
    service: http://localhost:{settings.ARGO_PORT}
    originRequest:
      noTLSVerify: true
  - service: http_status:404
"""
        with open(os.path.join(settings.FILE_PATH, 'tunnel.yml'), 'w') as file:
            file.write(tunnel_yaml)
    else:
        print("Use token connect to tunnel")

# 提取域名并生成链接
def extract_domains():
    argo_domain = ''

    if settings.ARGO_AUTH and settings.ARGO_DOMAIN:
        argo_domain = settings.ARGO_DOMAIN
        print('ARGO_DOMAIN:', argo_domain)
        generate_links(argo_domain)
    else:
        try:
            with open(os.path.join(settings.FILE_PATH, 'boot.log'), 'r', encoding='utf-8') as file:
                content = file.read()
                match = re.search(r'https://([^ ]+\.trycloudflare\.com)', content)
                if match:
                    argo_domain = match.group(1)
                    print('ArgoDomain:', argo_domain)
                    generate_links(argo_domain)
                else:
                    print('ArgoDomain not found, re-running bot to obtain ArgoDomain')
                    try:
                        subprocess.run("pkill -f 'bot tunnel'", shell=True)
                        print('Stopped existing bot process')
                    except Exception as e:
                        print(f'Error stopping bot process: {e}')

                    time.sleep(2)
                    os.remove(os.path.join(settings.FILE_PATH, 'boot.log'))

                    max_retries = 10
                    for attempt in range(max_retries):
                        print(f'Attempt {attempt + 1} of {max_retries}')
                        args = f"tunnel --edge-ip-version auto --no-autoupdate --protocol http2 --logfile {settings.FILE_PATH}/boot.log --loglevel info --url http://localhost:{settings.ARGO_PORT}"
                        try:
                            subprocess.run(f"nohup {settings.FILE_PATH}/bot {args} >/dev/null 2>&1 &", shell=True, check=True)
                            print('bot is running')
                            time.sleep(3)
                            with open(os.path.join(settings.FILE_PATH, 'boot.log'), 'r', encoding='utf-8') as file:
                                content = file.read()
                                match = re.search(r'https://([^ ]+\.trycloudflare\.com)', content)
                                if match:
                                    argo_domain = match.group(1)
                                    print('ArgoDomain:', argo_domain)
                                    generate_links(argo_domain)
                                    break
                            if attempt < max_retries - 1:
                                print('ArgoDomain not found, retrying...')
                                subprocess.run("pkill -f 'bot tunnel'", shell=True)
                                time.sleep(2)
                        except subprocess.CalledProcessError as e:
                            print(f"Error executing command: {e}")
                        except Exception as e:
                            print(f"Error: {e}")
                    else:
                        print("Failed to obtain ArgoDomain after maximum retries")
        except IndexError as e:
            print(f"IndexError while reading boot.log: {e}")
        except Exception as e:
            print(f"Error reading boot.log: {e}")

# 生成链接文件
def generate_links(argo_domain):
    meta_info = subprocess.run(['curl', '-s', 'https://speed.cloudflare.com/meta'], capture_output=True, text=True)
    meta_info = meta_info.stdout.split('"')
    ISP = f"{meta_info[25]}-{meta_info[17]}".replace(' ', '_').strip()

    time.sleep(2)
    VMESS = {
        "v": "2",
        "ps": f"{settings.NAME}-{ISP}",
        "add": settings.CFIP,
        "port": settings.CFPORT,
        "id": settings.UUID,
        "aid": "0",
        "scy": "none",
        "net": "ws",
        "type": "none",
        "host": argo_domain,
        "path": "/vmess-argo?ed=2048",
        "tls": "tls",
        "sni": argo_domain,
        "alpn": ""
    }

    list_txt = f"""
vless://{settings.UUID}@{settings.CFIP}:{settings.CFPORT}?encryption=none&security=tls&sni={argo_domain}&type=ws&host={argo_domain}&path=%2Fvless-argo%3Fed%3D2048#{settings.NAME}-{ISP}

vmess://{base64.b64encode(json.dumps(VMESS).encode('utf-8')).decode('utf-8')}

trojan://{settings.UUID}@{settings.CFIP}:{settings.CFPORT}?security=tls&sni={argo_domain}&type=ws&host={argo_domain}&path=%2Ftrojan-argo%3Fed%3D2048#{settings.NAME}-{ISP}
    """

    with open(os.path.join(settings.FILE_PATH, 'list.txt'), 'w', encoding='utf-8') as list_file:
        list_file.write(list_txt)

    sub_txt = base64.b64encode(list_txt.encode('utf-8')).decode('utf-8')
    with open(os.path.join(settings.FILE_PATH, 'sub.txt'), 'w', encoding='utf-8') as sub_file:
        sub_file.write(sub_txt)

    try:
        with open(os.path.join(settings.FILE_PATH, 'sub.txt'), 'rb') as file:
            sub_content = file.read()
        print(f"\n{sub_content.decode('utf-8')}")
    except FileNotFoundError:
        print(f"sub.txt not found")

    print(f'\n{settings.FILE_PATH}/sub.txt saved successfully')
    time.sleep(45)

    files_to_delete = ['npm', 'web', 'bot', 'boot.log', 'list.txt', 'config.json', 'tunnel.yml', 'tunnel.json']
    for file_to_delete in files_to_delete:
        file_path_to_delete = os.path.join(settings.FILE_PATH, file_to_delete)
        if os.path.exists(file_path_to_delete):
            try:
                os.remove(file_path_to_delete)
            except Exception as e:
                print(f"Error deleting {file_path_to_delete}: {e}")
        else:
            print(f"{file_path_to_delete} doesn't exist, skipping deletion")

    print('\033c', end='')
    print('App is running')
    print('Thank you for using this script, enjoy!')

# 定期访问项目页面
has_logged_empty_message = False

def visit_project_page():
    global has_logged_empty_message
    try:
        if not settings.PROJECT_URL or not settings.INTERVAL_SECONDS:
            if not has_logged_empty_message:
                print("URL or TIME variable is empty, Skipping visit web")
                has_logged_empty_message = True
            return

        response = requests.get(settings.PROJECT_URL)
        response.raise_for_status()
        print("Page visited successfully")
        print('\033c', end='')
    except requests.exceptions.RequestException as error:
        print(f"Error visiting project page: {error}")

def start_visit_thread():
    def run():
        while True:
            visit_project_page()
            time.sleep(settings.INTERVAL_SECONDS)

    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()
