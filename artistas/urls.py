from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ArtistaViewSet
from . import views
 



urlpatterns = [
    path('artistas/list/', views.ArtistaListView.as_view(), name='artistas_list'),
    path('artistas/create/', views.ArtistaCreateView.as_view(), name='artista_create'),
    path('artistas/<int:pk>/detail/', views.ArtistaDetailView.as_view(), name='artista_detail'),
    path('artistas/<int:pk>/update/', views.ArtistaUpdateView.as_view(), name='artista_update'),
    path('artistas/<int:pk>/delete/', views.ArtistaDeleteView.as_view(), name='artista_delete'),
    path('artistas/<int:pk>/mensagens/', views.lista_mensagens, name='lista_mensagens'),
    path('artista/<int:pk>/mensagens/criar/', views.criar_mensagem, name='criar_mensagem'),
    path('mensagens/<int:pk>/editar/', views.editar_mensagem, name='editar_mensagem'), 
    path('mensagens/<int:pk>/deletar/', views.deletar_mensagem, name='deletar_mensagem'),   
]
