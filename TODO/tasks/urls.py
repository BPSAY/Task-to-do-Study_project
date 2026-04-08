from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('stats/', views.task_stats, name='task_stats'),  # ← Новая строка
]