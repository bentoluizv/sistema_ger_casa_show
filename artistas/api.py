# gestao_eventos/artistas/api.py
from rest_framework import viewsets
from rest_framework.response import Response
from django_celery_beat.models import PeriodicTask
from celery.schedules import crontab
from .models import Artista
from .serializers import ArtistaSerializer
from .tasks import send_message
import json

class ArtistaViewSet(viewsets.ViewSet):
    def create(self, request):
        # Lógica para criar artista
        serializer = ArtistaSerializer(data=request.data)
        if serializer.is_valid():
            artista = serializer.save()
            # Agendar uma mensagem (exemplo)
            schedule_message(artista)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
def schedule_message(artista):
    # Criação de uma tarefa periódica
    PeriodicTask.objects.create(
        name=f'Envio de mensagem para {artista.nome}',
        task='artistas.tasks.send_message',
        schedule=crontab(minute=0, hour=0),   # Ajuste conforme necessário minute='0', hour='0'
        args=json.dumps([artista.id]),
    )

