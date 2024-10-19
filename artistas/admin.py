from django.contrib import admin
from .models import Artista, Mensagem 

@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'banco', 'tipo_chave_pix', 'chave_pix',)
    search_fields = ('nome', 'cpf', 'telefone',)

@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ('artista', 'data_envio', 'enviada')
    list_filter = ('enviada', 'data_envio')
    search_fields = ('artista__nome', 'conteudo')
    
