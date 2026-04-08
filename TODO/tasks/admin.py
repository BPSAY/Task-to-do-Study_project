from django.contrib import admin
from .models import Task, Category, Tag

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'status', 'category', 'due_date', 'is_completed']
    list_filter = ['priority', 'status', 'is_completed', 'category', 'tags', 'due_date']
    search_fields = ['title', 'description']
    list_editable = ['status', 'is_completed']
    filter_horizontal = ['tags']  # Красивый виджет для ManyToMany
    date_hierarchy = 'created_at'