from django.shortcuts import render
from django.db.models import Q, Count, Max, Min, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from .models import Task, Category, Tag


def task_list(request):
    """
    Отображение списка задач с фильтрацией и оптимизацией запросов.
    """
    # Базовый запрос
    tasks = Task.objects.all()
    
    # 🔹 Получаем параметры из GET-запроса
    search = request.GET.get('search', '')
    priority = request.GET.get('priority', '')
    status = request.GET.get('status', '')
    category_id = request.GET.get('category', '')
    tag_id = request.GET.get('tag', '')
    overdue = request.GET.get('overdue', '')
    
    # 🔹 Фильтрация с помощью Q-объектов (логическое ИЛИ для поиска)
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(tags__name__icontains=search)
        )
    
    # 🔹 Обычная фильтрация (логическое И)
    if priority:
        tasks = tasks.filter(priority=priority)
    if status:
        tasks = tasks.filter(status=status)
    if category_id:
        tasks = tasks.filter(category_id=category_id)
    if tag_id:
        tasks = tasks.filter(tags__id=tag_id)
    
    # 🔹 Фильтрация просроченных задач
    if overdue:
        tasks = tasks.filter(
            due_date__isnull=False,
            due_date__lt=timezone.now(),
            status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]
        )
    
    # 🔹 OPTIMIZATION: select_related для ForeignKey, prefetch_related для ManyToMany
    tasks = tasks.select_related('category').prefetch_related('tags').distinct()
    
    # 🔹 Получаем списки для фильтров в шаблоне
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    context = {
        'tasks': tasks,
        'categories': categories,
        'tags': tags,
        'filters': {
            'search': search,
            'priority': priority,
            'status': status,
            'category': category_id,
            'tag': tag_id,
            'overdue': overdue,
        }
    }
    return render(request, 'tasks/task_list.html', context)


def task_stats(request):
    """
    Статистика по задачам с использованием aggregate и annotate.
    """
    # 🔹 AGGREGATE: общие цифры по всем задачам
    stats = Task.objects.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status=Task.Status.DONE)),
        in_progress=Count('id', filter=Q(status=Task.Status.IN_PROGRESS)),
        todo=Count('id', filter=Q(status=Task.Status.TODO)),
        high_priority=Count('id', filter=Q(priority=Task.Priority.HIGH)),
        medium_priority=Count('id', filter=Q(priority=Task.Priority.MEDIUM)),
        low_priority=Count('id', filter=Q(priority=Task.Priority.LOW)),
        latest_due=Max('due_date', filter=Q(due_date__isnull=False)),
    )
    
    # 🔹 ANNOTATE: добавляем поля к каждому объекту категории
    categories_with_counts = Category.objects.annotate(
        task_count=Count('tasks'),
        completed_count=Count('tasks', filter=Q(tasks__status=Task.Status.DONE)),
        todo_count=Count('tasks', filter=Q(tasks__status=Task.Status.TODO)),
    ).order_by('-task_count')
    
    # 🔹 ANNOTATE: группировка по дате создания (последние 7 дней)
    tasks_by_date = Task.objects.annotate(
        created_date=TruncDate('created_at')
    ).values('created_date').annotate(
        count=Count('id'),
        completed=Count('id', filter=Q(status=Task.Status.DONE))
    ).order_by('-created_date')[:7]
    
    # 🔹 ANNOTATE: задачи по приоритетам
    tasks_by_priority = Task.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    
    context = {
        'stats': stats,
        'categories': categories_with_counts,
        'tasks_by_date': tasks_by_date,
        'tasks_by_priority': tasks_by_priority,
    }
    return render(request, 'tasks/task_stats.html', context)