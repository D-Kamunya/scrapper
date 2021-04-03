from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab  # scheduler
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scrapper.settings')

app = Celery('scrapper')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
# app.conf.beat_schedule = {
#     'scrap-indeed-jobs-24hrs': {
#         'task': 'scrap indeed jobs 24hrs',
#         'schedule': crontab(hour=0,minute=0)
#     }
# }
