
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BEcom.settings') 

app = Celery('BEcom') 
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')