from django.http import HttpResponse
import os

from .utils import FILE_PATH

def index(request):
    return HttpResponse('Hello, world')

def sub(request):
    try:
        with open(os.path.join(FILE_PATH, 'sub.txt'), 'rb') as file:
            content = file.read()
        return HttpResponse(content, content_type='text/plain; charset=utf-8')
    except FileNotFoundError:
        return HttpResponse('Error reading file', status=500)
