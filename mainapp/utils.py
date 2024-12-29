import os
import re
import shutil
import subprocess
import threading
import requests
import json
import time
import base64

# 环境变量设置
FILE_PATH = os.environ.get('FILE_PATH', './tmp')
PROJECT_URL = os.environ.get('URL', '')
INTERVAL_SECONDS = int(os.environ.get("TIME", 120))
UUID = os.environ.get('UUID', '6f4b65ef-94b9-4a93-b348-3c89eae6d353')
ARGO_DOMAIN = os.environ.get('ARGO_DOMAIN', '')
ARGO_AUTH = os.environ.get('ARGO_AUTH', '')
ARGO_PORT = int(os.environ.get('ARGO_PORT', 8001))
CFIP = os.environ.get('CFIP', 'linux.do')
CFPORT = int(os.environ.get('CFPORT', 443))
NAME = os.environ.get('NAME', 'Vls')
PORT = int(os.environ.get('SERVER_PORT') or os.environ.get('PORT') or 3000)

def generate_config():
    config = {
        "log": {
            "access": "none",
            "error": "none",
            "loglevel": "none"
        },
        "inbounds": [
            {
                "port": PORT,
                "protocol": "vless",
                "settings": {
                    "clients": [
                        {
                            "id": UUID,
                            "flow": "xtls-rprx-vision"
                        }
                    ],
                    "decryption": "none"
                },
                "streamSettings": {
                    "network": "tcp",
                    "security": "reality",
                    "realitySettings": {
                        "show": False,
                        "dest": f"{CFIP}:{CFPORT}",
                        "serverNames": [
                            CFIP,
                            "www.microsoft.com",
                            "www.amazon.com",
                            "www.apple.com",
                            "www.google.com"
                        ],
                        "privateKey": "2KZ4uouMKgI8nR-LDJNP1_MHisCJOmKB_7J2yKKKXVg",
                        "shortIds": [
                            "6ba85179e30d4fc2"
                        ]
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

    config_path = os.path.join(FILE_PATH, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def download_files_and_run():
    try:
        # 下载web文件
        web_url = "https://github.com/fscarmen2/X-for-web/raw/main/web"
        web_path = os.path.join(FILE_PATH, 'web')
        response = requests.get(web_url)
        with open(web_path, 'wb') as f:
            f.write(response.content)
        os.chmod(web_path, 0o777)
        print("Web file downloaded successfully")

        # 下载并解压npm文件
        npm_url = "https://github.com/fscarmen2/X-for-web/raw/main/npm.tar.gz"
        npm_path = os.path.join(FILE_PATH, 'npm.tar.gz')
        response = requests.get(npm_url)
        with open(npm_path, 'wb') as f:
            f.write(response.content)
        
        # 解压npm文件
        shutil.unpack_archive(npm_path, FILE_PATH)
        os.chmod(os.path.join(FILE_PATH, 'npm'), 0o777)
        os.remove(npm_path)
        print("NPM file downloaded and extracted successfully")

        # 下载bot文件
        bot_url = "https://github.com/fscarmen2/X-for-web/raw/main/bot"
        bot_path = os.path.join(FILE_PATH, 'bot')
        response = requests.get(bot_url)
        with open(bot_path, 'wb') as f:
            f.write(response.content)
        os.chmod(bot_path, 0o777)
        print("Bot file downloaded successfully")

        # 生成配置文件
        generate_config()
        print("Config generated successfully")

        # 启动web服务
        subprocess.Popen([web_path], cwd=FILE_PATH)
        print("Web service started")

    except Exception as e:
        print(f"Error in download_files_and_run: {str(e)}")

def extract_domains():
    try:
        with open(os.path.join(FILE_PATH, 'boot.log'), 'r') as f:
            log_content = f.read()

        # 提取域名
        domain_pattern = r'https://([^/\s]+)'
        domains = re.findall(domain_pattern, log_content)
        
        if domains:
            # 生成订阅内容
            sub_content = f"vless://{UUID}@{domains[0]}:{PORT}?encryption=none&flow=xtls-rprx-vision&security=reality&sni={CFIP}&fp=chrome&pbk=_YoaXqZPuTakxAzwQQyVsevnmXRfi2Qj-TYl4XLz2G0&sid=6ba85179e30d4fc2&type=tcp&headerType=none#{NAME}"
            
            # 保存到文件
            sub_path = os.path.join(FILE_PATH, 'sub.txt')
            with open(sub_path, 'w') as f:
                f.write(sub_content)
            print("Domains extracted and subscription content generated")

            # 保存域名列表
            list_path = os.path.join(FILE_PATH, 'list.txt')
            with open(list_path, 'w') as f:
                f.write('\n'.join(domains))
            print("Domain list saved")

    except Exception as e:
        print(f"Error in extract_domains: {str(e)}")

def visit_project_page():
    if PROJECT_URL:
        try:
            response = requests.get(PROJECT_URL)
            print(f"Visited project page: {response.status_code}")
        except Exception as e:
            print(f"Error visiting project page: {str(e)}")

def start_background_tasks():
    download_files_and_run()
    extract_domains()
    
    def visit_loop():
        while True:
            visit_project_page()
            time.sleep(INTERVAL_SECONDS)
    
    visit_thread = threading.Thread(target=visit_loop, daemon=True)
    visit_thread.start()

def start_server():
    # 创建目录（如果不存在）
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
        print(f"{FILE_PATH} has been created")
    else:
        print(f"{FILE_PATH} already exists")

    # 清理旧文件
    paths_to_delete = ['boot.log', 'list.txt','sub.txt', 'npm', 'web', 'bot', 'tunnel.yml', 'tunnel.json']
    for file in paths_to_delete:
        file_path = os.path.join(FILE_PATH, file)
        try:
            os.unlink(file_path)
            print(f"{file_path} has been deleted")
        except Exception as e:
            print(f"Skip Delete {file_path}")
    
    # 启动后台任务
    start_background_tasks()
