from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Sum
from .models import Disciplina, Professor, Grade, Horario, Student


def home_view(request):
    return render(request, 'core/Homepage.html')


def disciplinas(request):
    todas = Disciplina.objects.select_related('professor').all()
    return render(request, 'core/disciplinas.html', {'disciplinas': todas})


def disciplina_detalhe(request, pk):
    disciplina = get_object_or_404(Disciplina.objects.select_related('professor'), pk=pk)
    horarios   = disciplina.horarios.all().order_by('dia_semana', 'horario_inicio')
    avaliacoes = disciplina.avaliacoes.select_related('aluno__user').all()
    alunos_count = Student.objects.filter(grades__disciplinas=disciplina).distinct().count()
    return render(request, 'core/disciplina_detalhe.html', {
        'disciplina':   disciplina,
        'horarios':     horarios,
        'avaliacoes':   avaliacoes,
        'alunos_count': alunos_count,
    })


def professores(request):
    return render(request, 'core/professores.html')


def erro_404(request, exception=None):
    return render(request, 'core/erro_404.html', status=404)


def perfil(request):
    if request.user.is_authenticated:
        student_profile = get_object_or_404(Student, user=request.user)
        disciplinas_aluno = Disciplina.objects.filter(grades__aluno=student_profile)
    else:
        disciplinas_aluno = []
    return render(request, 'core/perfil.html', {'disciplinas_aluno': disciplinas_aluno})


def criar_avaliacao(request):
    todas_disciplinas = Disciplina.objects.all().order_by('nome')
    if request.method == 'POST':
        return redirect('perfil')
    return render(request, 'core/criar-avaliacao.html', {
        'disciplinas': todas_disciplinas
    })


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


def grade_view(request):
    student = Student.objects.first() 
    grade = Grade.objects.filter(aluno=student, semestre=1, ano=2026).first()
    horarios = []
    horas_range = []
    hora_min = 7
    total_rows = 0
    if grade:
        horarios = Horario.objects.filter(disciplina__in=grade.disciplinas.all())
        if horarios.exists():
            h_inicio = [h.horario_inicio.hour for h in horarios]
            h_fim = [h.horario_fim.hour for h in horarios]
            hora_min = min(h_inicio)
            hora_max = max(h_fim)
            horas_range = list(range(hora_min, hora_max + 1))
            total_rows = (hora_max - hora_min + 1) * 2

    return render(request, 'core/grade.html', {
        'grade': grade,
        'horarios': horarios,
        'horas_range': horas_range,
        'hora_min': hora_min,
        'total_rows': total_rows
    })


def matricula_view(request):
    todas_disciplinas = Disciplina.objects.select_related('professor').all()
    student = Student.objects.first() 
    grade = Grade.objects.filter(aluno=student, semestre=1, ano=2026).first()
    
    horarios = []
    horas_range = []
    hora_min = 7 
    total_rows = 20 
    matriculadas_ids = []
    total_creditos = 0
    
    if grade:
        matriculadas_ids = list(grade.disciplinas.values_list('id', flat=True))
        total_creditos = grade.disciplinas.aggregate(total=Sum('creditos'))['total'] or 0
        horarios = Horario.objects.filter(disciplina__in=grade.disciplinas.all())
        if horarios.exists():
            h_inicio = [h.horario_inicio.hour for h in horarios]
            h_fim = [h.horario_fim.hour for h in horarios]
            hora_min = min(min(h_inicio), 8)
            hora_max = max(max(h_fim), 18)
            horas_range = list(range(hora_min, hora_max + 1))
            total_rows = (hora_max - hora_min + 1) * 2
    context = {
        'disciplinas': todas_disciplinas,
        'matriculadas_ids': matriculadas_ids,
        'total_creditos_matriculados': total_creditos, 
        'horarios': horarios,
        'horas_range': horas_range,
        'hora_min': hora_min,
        'total_rows': total_rows,
    }
    return render(request, 'core/matricula.html', context)


def inscrever_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    student = Student.objects.first() #pra testar
    grade, created = Grade.objects.get_or_create(
        aluno=student,
        semestre=1,
        ano=2026
    )
    grade.disciplinas.add(disciplina)
    return redirect('matricula')