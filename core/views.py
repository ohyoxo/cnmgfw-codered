import os
import re
import shutil
import subprocess
import http.server
import socketserver
import threading
import requests
import json
import time
import base64
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["GET"])
def index(request):
    """主页视图"""
    return HttpResponse("Hello from Django!")

# 如果原Flask项目有其他视图函数，在这里添加对应的Django视图
