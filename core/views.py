from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Disciplina, Professor, Grade, Horario, Student
from .forms import UserEditForm, StudentEditForm, AvaliacaoForm


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


def avaliacoes(request):
    return render(request, 'core/avaliacoes.html')


def reportar_avaliacoes(request):
    return render(request, 'core/reportar-avaliacoes.html')


def erro_404(request, exception=None):
    return render(request, 'core/erro_404.html', status=404)

@login_required
def perfil(request):
    student = get_object_or_404(Student, user=request.user)
    disciplinas_aluno = Disciplina.objects.filter(
        grades__aluno=student
    ).select_related('professor').distinct()
    avaliacoes = student.avaliacoes.select_related('disciplina').all()
    total_creditos = disciplinas_aluno.aggregate(total=Sum('creditos'))['total'] or 0
    return render(request, 'core/perfil.html', {
        'student':          student,
        'disciplinas_aluno': disciplinas_aluno,
        'avaliacoes':        avaliacoes,
        'total_creditos':    total_creditos,
    })


@login_required
def editar_perfil(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        user_form    = UserEditForm(request.POST, instance=request.user)
        student_form = StudentEditForm(request.POST, request.FILES, instance=student)
        if user_form.is_valid() and student_form.is_valid():
            user_form.save()
            student_form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
    else:
        user_form    = UserEditForm(instance=request.user)
        student_form = StudentEditForm(instance=student)
    return render(request, 'core/editar_perfil.html', {
        'user_form':    user_form,
        'student_form': student_form,
    })


@login_required
def criar_avaliacao(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, student=student)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.aluno = student
            # Se já avaliou esta disciplina, atualiza
            Avaliacao.objects.update_or_create(
                aluno=student,
                disciplina=avaliacao.disciplina,
                defaults={
                    'nota':       avaliacao.nota,
                    'comentario': avaliacao.comentario,
                }
            )
            messages.success(request, 'Avaliação enviada com sucesso!')
            return redirect('perfil')
    else:
        disciplina_id = request.GET.get('disciplina')
        initial = {'disciplina': disciplina_id} if disciplina_id else {}
        form = AvaliacaoForm(student=student, initial=initial)
    return render(request, 'core/criar-avaliacao.html', {'form': form})


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


@login_required
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


@login_required
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


@login_required
def inscrever_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    student = Student.objects.first() # Mantido o mock padrão do seu projeto
    
    grade, created = Grade.objects.get_or_create(
        aluno=student,
        semestre=1,
        ano=2026
    )
    
    #  Aplica o validador antes de adicionar a matéria no banco
    tem_conflito, mensagem = grade.verificar_conflito_para_adicionar(disciplina)
    if tem_conflito:
        # Registra a mensagem de erro no sistema de mensagens do Django
        messages.error(request, mensagem)
        return redirect('matricula')
        
    grade.disciplinas.add(disciplina)
    return redirect('matricula')

def historico_grades(request):
    # ... sua lógica para pegar o aluno, grades e grade_ativa ...

    # 1. Defina a ordem dos horários e dias que você quer exibir
    lista_horarios = ["08:00", "10:00", "14:00", "16:00"]
    dias_semana = ["SEG", "TER", "QUA", "QUI", "SEX"]

    # 2. Monte uma estrutura linear simplificada para o template
    tabela_horarios = []
    
    for hora in lista_horarios:
        linha_atual = {
            'horario': hora,
            'dias': []  # Vai conter as disciplinas ordenadas de SEG a SEX
        }
        
        for dia in dias_semana:
            # Procure se existe alguma matéria nesse dia e horário específicos
            # (Adapte essa busca de acordo com seus Models)
            materia = disciplinas_da_grade_ativa.filter(
                horarios__dia=dia, 
                horarios__hora=hora
            ).first()
            
            # Adiciona o objeto da matéria ou None se estiver vago
            linha_atual['dias'].append(materia)
            
        tabela_horarios.append(linha_atual)

    context = {
        'grades': grades,
        'grade_ativa': grade_ativa,
        'disciplinas': disciplinas_da_grade_ativa,
        'tabela_horarios': tabela_horarios, # <--- Enviando a tabela pronta
    }
    
    return render(request, 'core/historico.html', context)

def minhas_avaliacoes_prof(request):
    return render(request, 'core/minhas-avaliacoes-prof.html')
