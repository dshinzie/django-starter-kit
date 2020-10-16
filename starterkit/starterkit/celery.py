import os
import celery
from django.conf import settings
from celery.signals import after_setup_logger, after_setup_task_logger


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'starterkit.settings')

# Celery configs
app = celery.Celery('starterkit')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


if __name__ == '__main__':
    app.start()
