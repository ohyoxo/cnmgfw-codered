from django.urls import path
from mainapp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sub/', views.sub, name='sub'),
]
