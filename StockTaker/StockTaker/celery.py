import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StockTaker.settings')

app = Celery('StockTaker')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
