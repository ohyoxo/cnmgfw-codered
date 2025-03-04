from .base import *  # 导入 base.py 中的基础设置
import os

# CodeRed Cloud 推荐设置
ALLOWED_HOSTS = [os.environ['VIRTUAL_HOST']]  # 从环境变量中获取域名
SECRET_KEY = os.environ['RANDOM_SECRET_KEY']  # 使用 CodeRed 提供的随机密钥
# 或者使用你之前生成的固定密钥：
# SECRET_KEY = 'k9z_xv2p7q8we5r4t3y6u1i0o_jn4m5l2c3b8a9sd_fghqwert'

# 数据库设置（如使用 MySQL/PostgreSQL）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 或 'django.db.backends.postgresql_psycopg2'
        'HOST': os.environ['DB_HOST'],
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'OPTIONS': {
            'ssl': {},
            'charset': 'utf8mb4',  # MySQL 需要
        },
    }
}

# 静态文件和媒体文件设置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 邮件设置（可选）
EMAIL_BACKEND = 'django_sendmail_backend.backends.EmailBackend'
