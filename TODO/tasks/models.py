from django.db import models
from django.db.models import Q

class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = 'low', '🟢 Низкий'
        MEDIUM = 'medium', '🟡 Средний'
        HIGH = 'high', '🔴 Высокий'
    
    class Status(models.TextChoices):
        TODO = 'todo', '📋 Нужно сделать'
        IN_PROGRESS = 'in_progress', '🔄 В процессе'
        DONE = 'done', '✅ Выполнено'
    
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Приоритет"
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.TODO,
        verbose_name="Статус"
    )
    
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Дедлайн")
    
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name="Категория"
    )
    
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='tasks',
        verbose_name="Теги"
    )
    
    is_completed = models.BooleanField(default=False, verbose_name="Выполнено")
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-priority', '-created_at']


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#3498db', help_text="Hex цвет, например #3498db")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"