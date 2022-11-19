import os

from celery import Celery

# 定义环境变量，这里是codebox.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codebox.settings')

app = Celery("codebox")

app.config_from_object('django.conf:settings', namespace='CELERY')

# 定义自动发现项目下的tasks.py文件
app.autodiscover_tasks()
