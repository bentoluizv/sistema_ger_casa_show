from django.db import models
from django.utils import timezone


TIPO_CHAVE_CHOICES = [
    ('cel', 'Celular'),
    ('cnpj', 'CNPJ'),
    ('email', 'E-mail'),
    ('cpf', 'CPF'),
]

class Artista(models.Model):

    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    banco = models.CharField(max_length=100)
    tipo_chave_pix = models.CharField(max_length=10, choices=TIPO_CHAVE_CHOICES, default='cel')
    chave_pix = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Mensagem(models.Model):
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE)
    conteudo = models.TextField()
    data_envio = models.DateTimeField(default=timezone.now)
    enviada = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Mensagem para {self.artista.nome} agendada para {self.data_envio}"
    
    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"