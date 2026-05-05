from django.shortcuts import render

# Create your views here.
def disciplinas(request):
    return render(request, 'core/disciplinas.html')

def professores(request):
    return render(request, 'core/professores.html')