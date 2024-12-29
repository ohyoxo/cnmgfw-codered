import os
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from . import utils

@require_http_methods(["GET"])
def index(request):
    return HttpResponse("Hello, world")

@require_http_methods(["GET"])
def sub(request):
    try:
        with open(os.path.join(settings.FILE_PATH, 'sub.txt'), 'rb') as file:
            content = file.read()
        return HttpResponse(content, content_type='text/plain; charset=utf-8')
    except FileNotFoundError:
        return HttpResponse('Error reading file', status=500)

def start_server():
    # 创建必要的目录
    if not os.path.exists(settings.FILE_PATH):
        os.makedirs(settings.FILE_PATH)
        print(f"{settings.FILE_PATH} has been created")
    
    # 清理旧文件
    paths_to_delete = ['boot.log', 'list.txt', 'sub.txt', 'npm', 'web', 'bot', 'tunnel.yml', 'tunnel.json']
    for file in paths_to_delete:
        file_path = os.path.join(settings.FILE_PATH, file)
        try:
            os.unlink(file_path)
        except:
            pass

    # 生成配置文件
    utils.generate_config()
    
    # 下载并运行文件
    architecture = utils.get_system_architecture()
    files_to_download = utils.get_files_for_architecture(architecture)
    
    if files_to_download:
        for file_info in files_to_download:
            try:
                utils.download_file(file_info['file_name'], file_info['file_url'])
            except Exception as e:
                print(f"Download {file_info['file_name']} failed: {e}")
                
        utils.authorize_files(['npm', 'web', 'bot'])
        
        # 运行服务
        try:
            subprocess.run(f"nohup {settings.FILE_PATH}/web -c {settings.FILE_PATH}/config.json >/dev/null 2>&1 &", 
                         shell=True, check=True)
            subprocess.run('sleep 1', shell=True)
            
            args = utils.get_cloud_flare_args()
            subprocess.run(f"nohup {settings.FILE_PATH}/bot {args} >/dev/null 2>&1 &", 
                         shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running services: {e}")

# 在Django启动时运行服务
import django.core.signals
django.core.signals.request_started.connect(start_server)
