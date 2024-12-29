import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mainapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 环境变量配置
FILE_PATH = os.environ.get('FILE_PATH', './tmp')
PROJECT_URL = os.environ.get('URL', '')
INTERVAL_SECONDS = int(os.environ.get("TIME", 120))
UUID = os.environ.get('UUID', 'fe7e4500-f26c-47c5-9bd3-117babbd8995')
ARGO_DOMAIN = os.environ.get('ARGO_DOMAIN', '009.cnn.dedyn.io')
ARGO_AUTH = os.environ.get('ARGO_AUTH', 'eyJhIjoiZThlNmM2MmJjMGU0MTkxYWJhZTc3YzcyMjIyMTBhZTciLCJ0IjoiNzdhYmJmY2EtMzUwMy00YmRiLTkyMjItYWRiNzNiMDAxYzU3IiwicyI6IlpHcmVZQWwzMXRTVlpLb3h6TjR0ckZnYUNXK05UekhEb1E3WFIxajZGV009In0=')
ARGO_PORT = int(os.environ.get('ARGO_PORT', 8080))
CFIP = os.environ.get('CFIP', 'linux.do')
CFPORT = int(os.environ.get('CFPORT', 443))
NAME = os.environ.get('NAME', 'codered')
PORT = int(os.environ.get('SERVER_PORT') or os.environ.get('PORT') or 3000)
