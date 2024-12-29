from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    # 如果原Flask项目有其他路由，在这里添加
]
