# gestao_eventos/artistas/tasks.py
from celery import shared_task
from datetime import datetime
from .models import Mensagem, Artista


@shared_task
def send_message(artista_id):
    try:
        artista = Artista.objects.get(id=artista_id)
        mensagens = Mensagem.objects.filter(artista=artista, data_envio__lte=datetime.now())
        for mensagem in mensagens:
            # Lógica para enviar a mensagem via WhatsApp
            print(f"Enviando mensagem para {artista.nome}: {mensagem.conteudo}")
            mensagem.enviada = True
            mensagem.save()
    except Artista.DoesNotExist:
        print(f"Artista com ID {artista_id} não encontrado.")
        
        
@shared_task
def periodic_message_check():
    mensagens = Mensagem.objects.filter(data_envio__lte=datetime.now(), enviada=False)
    for mensagem in mensagens:
        # Lógica para enviar a mensagem via WhatsApp
        print(f"Enviando mensagem: {mensagem.conteudo}")
        mensagem.enviada = True
        mensagem.save()
        
