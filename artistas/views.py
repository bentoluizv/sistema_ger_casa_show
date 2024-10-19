from django.contrib import messages
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from .forms import ArtistaForm, MensagemForm
from . import models, forms
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Artista, Mensagem
from django.views.generic.edit import CreateView

class ArtistaListView(ListView):
    model = Artista
    template_name = 'artistas_list.html'
    context_object_name = 'artistas'


@method_decorator(login_required(login_url= 'login'), name = 'dispatch')
class ArtistaCreateView(CreateView):
    model = Artista
    template_name = 'artista_create.html'
    form_class = forms.ArtistaForm
    success_url = reverse_lazy('artistas_list')
    
    def form_valid(self, form):
        print("Formulário válido, retornando página com erros")
        response = super().form_valid(form)
        messages.success(self.request, 'Artista criado com sucesso!')
        return response
    
    def form_invalid(self, form):  
        messages.error(self.request, 'Erro ao criar artista. Verifique os dados e tente novamente.')
        return self.render_to_response(self.get_context_data(form=form))
    
class ArtistaDetailView(DetailView):
    model = Artista
    template_name = 'artista_detail.html'
    context_object_name = 'artista'

@method_decorator(login_required(login_url= 'login'), name = 'dispatch')
class ArtistaUpdateView(UpdateView):
    model = Artista
    template_name = 'artista_update.html'
    form_class = forms.ArtistaForm
    success_url = reverse_lazy('artista_list')

@method_decorator(login_required (login_url='login'), name='dispatch')
class ArtistaDeleteView(DeleteView):
    model = Artista
    template_name = 'artista_delete.html'
    success_url = reverse_lazy('artista_list')
    
def criar_mensagem(request, pk):
    artista = get_object_or_404(Artista, pk=pk)
    print("Artista encontrado:", artista.nome)
    if request.method == 'POST':
        form = MensagemForm(request.POST)
        if form.is_valid():
            mensagem = form.save(commit=False)
            mensagem.artista = artista
            mensagem.save()
            return redirect('lista_mensagens', pk=artista.id)
    else:
        form = MensagemForm()
    return render(request, 'mensagens/criar_mensagem_para_artista.html', {'form': form, 'artista': artista})
   
def lista_mensagens(request, pk):
    artista = get_object_or_404(Artista, pk=pk)
    mensagens = Mensagem.objects.filter(artista=artista)  
    return render(request, 'mensagens/lista_mensagens.html', {'artista': artista, 'mensagens': mensagens})

def editar_mensagem(request, pk):
    mensagem = get_object_or_404(Mensagem, pk=pk)
    if request.method == 'POST':
        form = MensagemForm(request.POST, instance=mensagem)
        if form.is_valid():
            form.save()
            return redirect('lista_mensagens', pk=mensagem.artista.id)
    else:
        form = MensagemForm(instance=mensagem)
    return render(request, 'mensagens/editar_mensagem.html', {'form': form, 'mensagem': mensagem})
   
def deletar_mensagem(request, pk):
    mensagem = get_object_or_404(Mensagem, pk=pk)
    if request.method == 'POST':
        mensagem.delete()
        return redirect('lista_mensagens', pk=mensagem.artista.id)
    return render(request, 'mensagens/deletar_mensagem.html', {'mensagem': mensagem})
     
