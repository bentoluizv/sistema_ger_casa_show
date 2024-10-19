from django.test import TestCase
from unittest.mock import patch
from artistas.models import Artista, Mensagem
from artistas.serializers import ArtistaSerializer
from artistas.tasks import send_message, periodic_message_check
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from eventos.models import Evento
from django.urls import reverse
from artistas.forms import ArtistaForm, MensagemForm
from django.contrib.auth.models import User


class ArtistaSerializerTest(TestCase):
    def setUp(self):
        self.artista_data = {
            'nome': 'Artista Teste',
            'cpf': '123.456.789-00',
            'telefone': '(11) 98765-4321',
            'banco': 'Banco Teste',
            'tipo_chave_pix': 'cel',
            'chave_pix': '(11) 98765-4321'
        }
        self.artista = Artista.objects.create(**self.artista_data)

    def test_artista_serialization(self):
        serializer = ArtistaSerializer(self.artista)
        data = serializer.data
        self.assertEqual(data['nome'], self.artista.nome)
        self.assertEqual(data['id'], self.artista.id)
        # Testa se o campo 'celular' no serializer está correto
        self.assertEqual(data['telefone'], self.artista.telefone)

class CeleryTasksTest(TestCase):
    def setUp(self):
        self.artista = Artista.objects.create(
            nome="Artista Teste",
            cpf="123.456.789-00",
            telefone="(11) 98765-4321",
            banco="Banco Teste",
            tipo_chave_pix="cel",
            chave_pix="(11) 98765-4321"
        )
        self.mensagem = Mensagem.objects.create(
            artista=self.artista,
            conteudo="Mensagem Teste",
            data_envio=timezone.now(),
            enviada=False
        )

    @patch('artistas.tasks.print')
    def test_send_message_task(self, mock_print):
        send_message(self.artista.id)
        self.mensagem.refresh_from_db()  # Atualiza a mensagem do banco
        self.assertTrue(self.mensagem.enviada)
        mock_print.assert_called_with(f"Enviando mensagem para {self.artista.nome}: {self.mensagem.conteudo}")

    @patch('artistas.tasks.print')
    def test_periodic_message_check(self, mock_print):
        periodic_message_check()
        self.mensagem.refresh_from_db()
        self.assertTrue(self.mensagem.enviada)
        mock_print.assert_called_with(f"Enviando mensagem: {self.mensagem.conteudo}")
 
class AgendamentoMensagemTest(TestCase):
    def setUp(self):
        self.artista = Artista.objects.create(
            nome="Artista Teste",
            cpf="123.456.789-00",
            telefone="(11) 98765-4321",
            banco="Banco Teste",
            tipo_chave_pix="cel",
            chave_pix="(11) 98765-4321"
        )

    def test_mensagem_agendada(self):
        # Criando uma mensagem agendada para o futuro
        futuro = timezone.now() + timedelta(days=1)
        mensagem_futura = Mensagem.objects.create(
            artista=self.artista,
            conteudo="Mensagem Futura",
            data_envio=futuro,
            enviada=False
        )

        # Rodando a task antes do tempo agendado
        periodic_message_check()
        mensagem_futura.refresh_from_db()
        self.assertFalse(mensagem_futura.enviada)

        # Atualizando a data para simular o envio no tempo correto
        mensagem_futura.data_envio = timezone.now()
        mensagem_futura.save()

        # Executando novamente a task para enviar
        periodic_message_check()
        mensagem_futura.refresh_from_db()
        self.assertTrue(mensagem_futura.enviada)
        
class ArtistaModelValidationTest(TestCase):
    def test_campo_obrigatorio_nome(self):
        with self.assertRaises(ValidationError):
            artista = Artista(nome="", cpf="123.456.789-00", banco="Banco Teste", chave_pix="(11) 98765-4321")
            artista.full_clean()  # Dispara validações

class EventoModelValidationTest(TestCase):
    def test_evento_sem_data(self):
        artista = Artista.objects.create(nome="Artista Teste", cpf="123.456.789-00", banco="Banco Teste", chave_pix="(11) 98765-4321")
        with self.assertRaises(ValidationError):
            evento = Evento(artista=artista, data=None, horario=timezone.now().time())
            evento.full_clean()  # Dispara validações
            
class ArtistaModelMaxLengthTest(TestCase):
    def test_nome_max_length(self):
        artista = Artista(nome="A" * 101, cpf="123.456.789-00", banco="Banco Teste", chave_pix="(11) 98765-4321")
        with self.assertRaises(ValidationError):
            artista.full_clean()  # Tenta validar

    def test_chave_pix_max_length(self):
        artista = Artista(nome="Artista Teste", cpf="123.456.789-00", banco="Banco Teste", chave_pix="X" * 101)
        with self.assertRaises(ValidationError):
            artista.full_clean()
            
class ArtistaChavePixTest(TestCase):
    def test_chave_pix_tipo_celular(self):
        artista = Artista.objects.create(nome="Artista Celular", cpf="123.456.789-00", banco="Banco Teste", tipo_chave_pix="cel", chave_pix="(11) 98765-4321")
        self.assertEqual(artista.tipo_chave_pix, "cel")
        self.assertEqual(artista.chave_pix, "(11) 98765-4321")

    def test_chave_pix_tipo_email(self):
        artista = Artista.objects.create(nome="Artista Email", cpf="123.456.789-00", banco="Banco Teste", tipo_chave_pix="email", chave_pix="artista@email.com")
        self.assertEqual(artista.tipo_chave_pix, "email")
        self.assertEqual(artista.chave_pix, "artista@email.com")
        
class CeleryTasksAdditionalTests(TestCase):
    def setUp(self):
        self.artista = Artista.objects.create(
            nome="Artista Teste",
            cpf="123.456.789-00",
            telefone="(11) 98765-4321",
            banco="Banco Teste",
            tipo_chave_pix="cel",
            chave_pix="(11) 98765-4321"
        )
        self.mensagem = Mensagem.objects.create(
            artista=self.artista,
            conteudo="Mensagem Teste",
            data_envio=timezone.now(),
            enviada=False
        )

    def test_nao_reenvia_mensagem_ja_enviada(self):
        self.mensagem.enviada = True
        self.mensagem.save()

        periodic_message_check()
        self.mensagem.refresh_from_db()
        self.assertTrue(self.mensagem.enviada)  # Confirma que ela não foi reenviada

class EventoModelTest(TestCase):
    def setUp(self):
        self.artista = Artista.objects.create(
            nome="Artista Teste",
            cpf="123.456.789-00",
            telefone="(11) 98765-4321",
            banco="Banco Teste",
            tipo_chave_pix="cel",
            chave_pix="(11) 98765-4321"
        )
        self.evento = Evento.objects.create(
            artista=self.artista,
            data=timezone.now().date(),
            horario=timezone.now().time(),
            descricao="Evento Teste"
        )

    def test_evento_str(self):
        # Testando o método __str__, linha 17
        self.assertEqual(str(self.evento), self.artista.nome)

    def test_evento_formatted_data(self):
        # Testando o método formatted_data, linha 20
        self.assertEqual(self.evento.formatted_data(), self.evento.data.strftime('%d-%m-%Y'))

    def test_evento_formatted_horario(self):
        # Testando o método formatted_horario, linha 23
        self.assertEqual(self.evento.formatted_horario(), self.evento.horario.strftime('%H-%M'))
        
class ArtistaCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.valid_data = {
            'nome': 'Novo Artista',
            'cpf': '123.456.789-09',  # CPF no formato válido
            'telefone': '(11) 98765-4321',
            'banco': 'Banco Teste',
            'tipo_chave_pix': 'cel',
            'chave_pix': '(11) 98765-4321'
        }
        self.invalid_data = {
            'nome': '',  # Nome vazio para garantir que é inválido
            'cpf': '123',  # CPF claramente inválido
        }

    def test_artista_create_view_valid(self):
        response = self.client.post(reverse('artista_create'), self.valid_data)
        self.assertEqual(response.status_code, 302)  # Redireciona após sucesso
        self.assertRedirects(response, reverse('artistas_list'))
        self.assertTrue(Artista.objects.filter(nome='Novo Artista').exists())  # O artista deve ser criado

    def test_artista_create_view_invalid(self):
        response = self.client.post(reverse('artista_create'), self.invalid_data)
        self.assertEqual(response.status_code, 200)  # Página deve ser renderizada novamente com erros
        self.assertTemplateUsed(response, 'artista_create.html')   
        self.assertIn('form', response.context)  # O formulário com erros deve estar no contexto
        self.assertFalse(Artista.objects.filter(nome='').exists())  # Nenhum artista inválido foi criado
