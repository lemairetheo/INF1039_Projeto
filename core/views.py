from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Disciplina, Professor


def home_view(request):
    return render(request, 'core/Homepage.html')


def disciplinas(request):
    todas = Disciplina.objects.select_related('professor').all()
    return render(request, 'core/disciplinas.html', {'disciplinas': todas})


def disciplina_detalhe(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    return render(request, 'core/disciplina_detalhe.html', {'disciplina': disciplina})


def professores(request):
    return render(request, 'core/professores.html')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/cadastro1.html', {'form': form})
