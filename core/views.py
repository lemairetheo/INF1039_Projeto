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

from django.db.models import Count # Certifique-se de importar o Count no topo do arquivo junto ao Sum

def historico_grades_view(request):
    # Se o usuário estiver logado, usamos request.user.student, senão usamos o mock para testes
    if request.user.is_authenticated:
        try:
            student = request.user.student
        except Student.DoesNotExist:
            student = Student.objects.first()
    else:
        student = Student.objects.first() # Padrão usado nas suas outras views de teste
    
    # 1. Busca TODAS as grades históricas do aluno
    # Usa o annotate para calcular os totais direto no banco de dados
    grades = Grade.objects.filter(aluno=student).annotate(
        total_disciplinas=Count('disciplinas'),
        total_creditos=Sum('disciplinas__creditos')
    ).order_by('-ano', '-semestre')
    
    # 2. Captura a grade ativa (a primeira selecionada por padrão ou a mais recente)
    # Se o usuário clicar em uma específica via GET (?grade_id=X), carregamos ela.
    grade_id = request.GET.get('grade_id')
    if grade_id:
        grade_ativa = grades.filter(id=grade_id).first()
    else:
        grade_ativa = grades.first()

    # 3. Mapeia os horários da grade ativa para alimentar a tabela semanal
    # Cria um dicionário para o template buscar rapidamente por "dia_hora"
    grade_agenda = {}
    disciplinas_da_grade = []
    
    if grade_ativa:
        disciplinas_da_grade = grade_ativa.disciplinas.all().select_related('professor').prefetch_related('horarios')
        
        # Alimenta a matriz de horários para a tabela
        for disciplina in disciplinas_da_grade:
            for horario in disciplina.horarios.all():
                # Formato da chave: 'DIA-HORA_INICIO' -> Ex: '2-09:00:00'
                chave = f"{horario.dia_semana}-{horario.horario_inicio.strftime('%H:%M')}"
                grade_agenda[chave] = disciplina.nome

    # Cria a lista de horas que o CSS espera 
    horas_grade = ['09:00', '15:00'] 

    context = {
        'grades': grades,
        'grade_ativa': grade_ativa,
        'disciplinas': disciplinas_da_grade,
        'grade_agenda': grade_agenda,
        'horas_grade': horas_grade,
    }
    return render(request, 'core/historico.html', context)
