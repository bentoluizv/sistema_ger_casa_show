from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
  
#módulo conf.do django 
os. environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
#cria instância do celery
app = Celery('gestao_eventos')
#carrega as conf.do celery no django
app.config_from_object('django.conf:settings', namespace='CELERY')
#carrega task de todos os aplicativos registrados.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task():
    print('Request: {0!r}'.format(self.request))
