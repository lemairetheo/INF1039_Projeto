from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.core.exceptions import PermissionDenied
from django.contrib import messages
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
        'horarios':      horarios,
        'avaliacoes':    avaliacoes,
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
    student = Student.objects.first() # Mantido o mock padrão do seu projeto
    
    grade, created = Grade.objects.get_or_create(
        aluno=student,
        semestre=1,
        ano=2026
    )
    
    # [PROTEÇÃO MD1] Aplica o validador antes de adicionar a matéria no banco
    tem_conflito, mensagem = grade.verificar_conflito_para_adicionar(disciplina)
    if tem_conflito:
        # Registra a mensagem de erro no sistema de mensagens do Django
        messages.error(request, mensagem)
        return redirect('matricula')
        
    grade.disciplinas.add(disciplina)
    return redirect('matricula')


def historico_grades_view(request):
    if request.user.is_authenticated:
        try:
            student = request.user.student
        except Student.DoesNotExist:
            student = Student.objects.first()
    else:
        student = Student.objects.first() 
    
    # 1. Coleta o histórico agregando valores direto no banco
    grades = Grade.objects.filter(aluno=student).annotate(
        total_disciplinas=Count('disciplinas'),
        total_creditos=Sum('disciplinas__creditos')
    ).order_by('-ano', '-semestre')
    
    # 2. [SEGURANÇA TAREFA M2] Validação estrita do ID via parâmetro GET
    grade_id = request.GET.get('grade_id')
    if grade_id:
        grade_ativa = grades.filter(id=grade_id).first()
        
        # Bloqueio de ID Scan: Se a grade existe mas não pertence a este aluno
        if not grade_ativa and Grade.objects.filter(id=grade_id).exists():
            raise PermissionDenied("Você não tem autorização para visualizar este histórico de horários.")
    else:
        grade_ativa = grades.first()

    # 3. [MOTOR DINÂMICO TAREFA MD1] Processamento de Matriz e Colisões Complexas
    matriz_horarios = {}
    horas_ordenadas = []
    conflitos_detectados = []
    disciplinas_da_grade = []
    dias_semana_codigos = ['2', '3', '4', '5', '6'] 

    if grade_ativa:
        disciplinas_da_grade = grade_ativa.disciplinas.all().select_related('professor').prefetch_related('horarios')
        conflitos_detectados = grade_ativa.mapa_de_conflitos
        
        # Extrai os blocos horários exatos para construir as linhas dinamicamente
        todos_horarios = Horario.objects.filter(
            disciplina__in=disciplinas_da_grade
        ).order_by('horario_inicio')
        
        horas_ordenadas = sorted(list(set(h.horario_inicio.strftime('%H:%M') for h in todos_horarios)))
        
        # Inicializa a matriz para evitar erros de KeyError no template
        for hora in horas_ordenadas:
            matriz_horarios[hora] = {dia: [] for dia in dias_semana_codigos}
            
        # Alimenta a matriz permitindo múltiplas matérias na mesma célula (colisão controlada)
        for h in todos_horarios:
            hora_str = h.horario_inicio.strftime('%H:%M')
            matriz_horarios[hora_str][h.dia_semana].append(h.disciplina)

    context = {
        'grades': grades,
        'grade_ativa': grade_ativa,
        'disciplinas': disciplinas_da_grade,
        'conflitos': conflitos_detectados,
        'matriz_horarios': matriz_horarios,
        'horas_ordenadas': horas_ordenadas,
        'dias_semana_codigos': dias_semana_codigos,
    }
    return render(request, 'core/historico.html', context)

def minhas_avaliacoes_prof(request):
    return render(request, 'core/minhas-avaliacoes-prof.html')