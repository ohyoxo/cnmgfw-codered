from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
import os

def index(request):
    return HttpResponse("Hello, world")

def sub(request):
    sub_file_path = os.path.join(settings.FILE_PATH, 'sub.txt')
    try:
        with open(sub_file_path, 'rb') as file:
            content = file.read()
        return HttpResponse(content, content_type='text/plain; charset=utf-8')
    except FileNotFoundError:
        return HttpResponse("Error reading file", status=500)
