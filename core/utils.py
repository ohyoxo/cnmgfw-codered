import os
import shutil
from django.conf import settings

def initialize_environment():
    """初始化环境，创建必要的目录并清理旧文件"""
    
    # 创建目录
    if not os.path.exists(settings.FILE_PATH):
        os.makedirs(settings.FILE_PATH)
        print(f"{settings.FILE_PATH} has been created")
    else:
        print(f"{settings.FILE_PATH} already exists")

    # 清理旧文件
    paths_to_delete = [
        'boot.log', 
        'list.txt',
        'sub.txt', 
        'npm', 
        'web', 
        'bot', 
        'tunnel.yml', 
        'tunnel.json'
    ]
    
    for file in paths_to_delete:
        file_path = os.path.join(settings.FILE_PATH, file)
        try:
            os.unlink(file_path)
            print(f"{file_path} has been deleted")
        except Exception as e:
            print(f"Skip Delete {file_path}")
