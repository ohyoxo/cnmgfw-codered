import os
import re
import json
import time
import base64
import shutil
import requests
import subprocess
import threading
from django.conf import settings

def get_system_architecture():
    arch = os.uname().machine
    if 'arm' in arch or 'aarch64' in arch or 'arm64' in arch:
        return 'arm'
    return 'amd'

def download_file(file_name, file_url):
    file_path = os.path.join(settings.FILE_PATH, file_name)
    with requests.get(file_url, stream=True) as response, open(file_path, 'wb') as file:
        shutil.copyfileobj(response.raw, file)

def get_files_for_architecture(architecture):
    if architecture == 'arm':
        return [
            {'file_name': 'npm', 'file_url': 'https://github.com/eooce/test/releases/download/arm64/swith'},
            {'file_name': 'web', 'file_url': 'https://github.com/eooce/test/releases/download/arm64/web'},
            {'file_name': 'bot', 'file_url': 'https://github.com/eooce/test/releases/download/arm64/bot'},
        ]
    elif architecture == 'amd':
        return [
            {'file_name': 'npm', 'file_url': 'https://github.com/eooce/test/releases/download/amd64/npm'},
            {'file_name': 'web', 'file_url': 'https://github.com/eooce/test/releases/download/amd64/web'},
            {'file_name': 'bot', 'file_url': 'https://github.com/eooce/test/releases/download/amd64/bot'},
        ]
    return []

def authorize_files(file_paths):
    new_permissions = 0o775
    for relative_file_path in file_paths:
        absolute_file_path = os.path.join(settings.FILE_PATH, relative_file_path)
        try:
            os.chmod(absolute_file_path, new_permissions)
            print(f"Empowerment success for {absolute_file_path}: {oct(new_permissions)}")
        except Exception as e:
            print(f"Empowerment failed for {absolute_file_path}: {e}")

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

def generate_config():
    config = {
        "log": {
            "access": "/dev/null",
            "error": "/dev/null",
            "loglevel": "none"
        },
        "inbounds": [
            {
                "port": settings.ARGO_PORT,
                "protocol": "vless",
                "settings": {
                    "clients": [
                        {
                            "id": settings.UUID,
                            "flow": ""
                        }
                    ],
                    "decryption": "none",
                    "fallbacks": [
                        {
                            "dest": 3001
                        },
                        {
                            "path": "/vless-argo",
                            "dest": 3002
                        },
                        {
                            "path": "/vmess-argo",
                            "dest": 3003
                        },
                        {
                            "path": "/trojan-argo",
                            "dest": 3004
                        }
                    ]
                },
                "streamSettings": {
                    "network": "tcp"
                }
            },
            {
                "port": 3001,
                "listen": "127.0.0.1",
                "protocol": "vless",
                "settings": {
                    "clients": [
                        {
                            "id": settings.UUID,
                            "flow": "xtls-rprx-vision"
                        }
                    ],
                    "decryption": "none",
                    "fallbacks": []
                },
                "streamSettings": {
                    "network": "tcp",
                    "security": "reality",
                    "realitySettings": {
                        "show": False,
                        "dest": f"{settings.CFIP}:{settings.CFPORT}",
                        "xver": 0,
                        "serverNames": [
                            settings.CFIP
                        ],
                        "privateKey": "2KZ4uouMKgI8nR-LDJNP1_MHisCJOmKB_LpZXNRf8E4",
                        "minClientVer": "",
                        "maxClientVer": "",
                        "maxTimeDiff": 0,
                        "shortIds": [
                            "6ba85179e30d4fc2"
                        ]
                    }
                }
            },
            {
                "port": 3002,
                "listen": "127.0.0.1",
                "protocol": "vless",
                "settings": {
                    "clients": [
                        {
                            "id": settings.UUID
                        }
                    ],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "none",
                    "wsSettings": {
                        "path": "/vless-argo"
                    }
                }
            },
            {
                "port": 3003,
                "listen": "127.0.0.1",
                "protocol": "vmess",
                "settings": {
                    "clients": [
                        {
                            "id": settings.UUID
                        }
                    ]
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "none",
                    "wsSettings": {
                        "path": "/vmess-argo"
                    }
                }
            },
            {
                "port": 3004,
                "listen": "127.0.0.1",
                "protocol": "trojan",
                "settings": {
                    "clients": [
                        {
                            "password": settings.UUID
                        }
                    ]
                },
                "streamSettings": {
                    "network": "ws",
                    "security": "none",
                    "wsSettings": {
                        "path": "/trojan-argo"
                    }
                }
            }
        ],
        "outbounds": [
            {
                "protocol": "freedom"
            }
        ]
    }
    
    with open(os.path.join(settings.FILE_PATH, 'config.json'), 'w', encoding='utf-8') as config_file:
        json.dump(config, config_file, ensure_ascii=False, indent=2)

def generate_links():
    def get_domain():
        if settings.ARGO_AUTH and settings.ARGO_DOMAIN:
            return settings.ARGO_DOMAIN
        
        log_file = os.path.join(settings.FILE_PATH, 'boot.log')
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.read()
                pattern = r'https://[^.]+\..*\.'
                matches = re.findall(pattern, logs)
                if matches:
                    return matches[-1][:-1]
        except:
            pass
        return None

    def write_list(domain):
        if not domain:
            return
            
        vless = f"vless://{settings.UUID}@{settings.CFIP}:443?encryption=none&security=reality&sni={settings.CFIP}&fp=chrome&pbk=jNXHhi6c8g9JXS4gJtkUYw5_iODwHg_NXjCeKmpyKCY&sid=6ba85179e30d4fc2&type=tcp&flow=xtls-rprx-vision#{settings.NAME}-Reality\n"
        vless_ws = f"vless://{settings.UUID}@{domain}:443?encryption=none&security=tls&type=ws&host={domain}&path=/vless-argo#{settings.NAME}-Vless\n"
        vmess = json.dumps({
            "v": "2",
            "ps": f"{settings.NAME}-Vmess",
            "add": domain,
            "port": 443,
            "id": settings.UUID,
            "aid": 0,
            "scy": "none",
            "net": "ws",
            "type": "none",
            "host": domain,
            "path": "/vmess-argo",
            "tls": "tls",
            "sni": "",
            "alpn": ""
        })
        vmess_base64 = "vmess://" + base64.b64encode(vmess.encode('utf-8')).decode('utf-8') + "\n"
        trojan = f"trojan://{settings.UUID}@{domain}:443?security=tls&type=ws&host={domain}&path=/trojan-argo#{settings.NAME}-Trojan"

        links = f"{vless}{vless_ws}{vmess_base64}{trojan}"
        with open(os.path.join(settings.FILE_PATH, 'list.txt'), 'w', encoding='utf-8') as f:
            f.write(links)
        
        links_bytes = links.encode('utf-8')
        encoded_links = base64.b64encode(links_bytes).decode('utf-8')
        with open(os.path.join(settings.FILE_PATH, 'sub.txt'), 'w', encoding='utf-8') as f:
            f.write(encoded_links)

    def check_domain():
        while True:
            domain = get_domain()
            if domain:
                write_list(domain)
                break
            time.sleep(settings.INTERVAL_SECONDS)

    threading.Thread(target=check_domain).start()
