from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages
from .models import Disciplina, Professor, Matricula, Turma, Avaliacao, Student, Denuncia
from .forms import UserEditForm, StudentEditForm, AvaliacaoForm


# ── Helpers ────────────────────────────────────────────────────────────────────

class _VirtualGrade:
    """Simulates the old Grade object for the historico template."""
    def __init__(self, ano, semestre, disciplinas, student):
        self.id       = f"{ano}-{semestre}"
        self.ano      = ano
        self.semestre = semestre
        self.aluno    = student
        self._disciplinas = list(disciplinas)

    @property
    def disciplinas(self):
        return self

    def count(self):
        return len(self._disciplinas)

    def __iter__(self):
        return iter(self._disciplinas)

    def all(self):
        return self._disciplinas


# ── Views ──────────────────────────────────────────────────────────────────────

def home_view(request):
    return render(request, 'core/Homepage.html')


def disciplinas(request):
    todas = Disciplina.objects.all()
    return render(request, 'core/disciplinas.html', {'disciplinas': todas})


def disciplina_detalhe(request, pk):
    disciplina   = get_object_or_404(Disciplina, pk=pk)
    turmas       = disciplina.turma_disciplina.select_related('professor').all()
    avaliacoes   = disciplina.avaliacoes.select_related('aluno__user').all()
    alunos_count = Student.objects.filter(
        grades__disciplina=disciplina
    ).distinct().count()
    return render(request, 'core/disciplina_detalhe.html', {
        'disciplina':   disciplina,
        'turmas':       turmas,
        'avaliacoes':   avaliacoes,
        'alunos_count': alunos_count,
    })

def professores(request):
    return render(request, 'core/professores.html')


def avaliacoes(request):
    return render(request, 'core/avaliacoes.html')


#@login_required
def reportar_avaliacoes(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)

    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        descricao = request.POST.get('descricao', '').strip()

        if motivo == 'outros' and not descricao:
            messages.error(request, "A descrição é obrigatória quando o motivo for 'Outros'.")
            return render(request, 'core/reportar-avaliacoes.html', {'avaliacao': avaliacao})

        Denuncia.objects.create(
            avaliacao=avaliacao,
            motivo=motivo,
            descricao=descricao
        )
        messages.success(request, 'Avaliação reportada com sucesso! Analisaremos o caso.')
        return redirect('Avaliações') 
    return render(request, 'core/reportar-avaliacoes.html', {'avaliacao': avaliacao})


def erro_404(request, exception=None):
    return render(request, 'core/erro_404.html', status=404)


@login_required
def perfil(request):
    student = get_object_or_404(Student, user=request.user)
    disciplinas_aluno = Disciplina.objects.filter(
        matricula_disciplina__aluno=student
    ).distinct()
    avaliacoes_aluno = student.avaliacoes.select_related('disciplina').all()
    total_creditos   = disciplinas_aluno.aggregate(total=Sum('creditos'))['total'] or 0
    return render(request, 'core/perfil.html', {
        'student':           student,
        'disciplinas_aluno': disciplinas_aluno,
        'avaliacoes':        avaliacoes_aluno,
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
    student  = Student.objects.first()
    matriculas = Matricula.objects.filter(aluno=student, semestre=1, ano=2026)
    disc_ids = matriculas.values_list('disciplina_id', flat=True)
    turmas   = Turma.objects.filter(
        disciplina_id__in=disc_ids
    ).select_related('disciplina', 'professor').order_by('dia_semana', 'horario')

    return render(request, 'core/grade.html', {
        'turmas': turmas,
        'has_matriculas': matriculas.exists(),
    })


def matricula_view(request):
    todas_disciplinas = Disciplina.objects.all()
    student           = Student.objects.first()
    matriculas        = Matricula.objects.filter(aluno=student, semestre=1, ano=2026)
    matriculadas_ids  = list(matriculas.values_list('disciplina_id', flat=True))
    total_creditos    = (
        Disciplina.objects.filter(id__in=matriculadas_ids)
        .aggregate(total=Sum('creditos'))['total'] or 0
    )
    turmas = Turma.objects.filter(
        disciplina_id__in=matriculadas_ids
    ).select_related('disciplina', 'professor').order_by('dia_semana', 'horario')

    context = {
        'disciplinas':                 todas_disciplinas,
        'matriculadas_ids':            matriculadas_ids,
        'total_creditos_matriculados': total_creditos,
        'turmas':                      turmas,
    }
    return render(request, 'core/matricula.html', context)


@login_required
def inscrever_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    student    = Student.objects.first()

    if request.method == 'POST':
        Matricula.objects.get_or_create(
            aluno=student,
            disciplina=disciplina,
            defaults={'semestre': 1, 'ano': 2026}
        )
    return redirect('matricula')


@login_required
def cancelar_inscricao(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    student    = Student.objects.first()
    if request.method == 'POST':
        Matricula.objects.filter(aluno=student, disciplina=disciplina).delete()
    return redirect('matricula')


@login_required
def historico_grades(request):
    try:
        aluno = request.user.student
    except Student.DoesNotExist:
        return render(request, 'core/historico.html', {
            'error_message': "Seu usuário não possui um perfil de aluno cadastrado."
        })

    matriculas = aluno.grades.select_related('disciplina').order_by('-ano', '-semestre')

    # Group by (ano, semestre) → build virtual grade objects
    from collections import defaultdict
    grade_dict = defaultdict(list)
    order      = []
    for m in matriculas:
        key = (m.ano, m.semestre)
        if key not in grade_dict:
            order.append(key)
        grade_dict[key].append(m.disciplina)

    grades = [
        _VirtualGrade(ano, sem, discs, aluno)
        for (ano, sem), discs in ((k, grade_dict[k]) for k in order)
    ]

    # Determine active grade
    grade_id  = request.GET.get('grade_id')
    grade_ativa = None
    if grade_id:
        for g in grades:
            if g.id == grade_id:
                grade_ativa = g
                break
    if grade_ativa is None and grades:
        grade_ativa = grades[0]

    disciplinas_da_grade = list(grade_ativa) if grade_ativa else []

    context = {
        'grades':      grades,
        'grade_ativa': grade_ativa,
        'disciplinas': disciplinas_da_grade,
        'aluno':       aluno,
    }
    return render(request, 'core/historico.html', context)


def minhas_avaliacoes_prof(request, id_professor, ):
    qtd_avaliacoes = Avaliacao.objects.count()

    return render(request, 'core/minhas-avaliacoes-prof.html', {
        'disciplinas': disciplinas,
        'avaliacoes': avaliacoes,
        'qtd_avaliacoes': qtd_avaliacoes,
        'nota_professor': nota_professor,
        'nota_disciplina': nota_disciplina,
        }
    )


def detalhes_disciplina(request):
    disciplina = {
        "id": 1,
        "nome": "Cálculo I",
        "creditos": 4,
        "descricao": "Limites, derivadas e integrais de funções de uma variável.",
        "departamento": "MAT",
    }

    turmas = [
        {
            "id": 1,
            "professor": {"nome": "Dra. Helena Vasconcelos"},
            "horario": "SEG 09:00–11:00, QUA 09:00–11:00",
            "vagas_ocupadas": 28,
            "vagas_totais": 40,
            "nota_media": 4.5,
        },
        {
            "id": 2,
            "professor": {"nome": "Dr. Ricardo Almeida"},
            "horario": "TER 13:00–15:00, QUI 13:00–15:00",
            "vagas_ocupadas": 34,
            "vagas_totais": 40,
            "nota_media": 4.2,
        },
        {
            "id": 3,
            "professor": {"nome": "Prof. Fernanda Costa"},
            "horario": "SEG 19:00–21:00, QUA 19:00–21:00",
            "vagas_ocupadas": 15,
            "vagas_totais": 40,
            "nota_media": 4.8,
        },
    ]

    avaliacoes = [
        {"data": "29/04/2026", "comentario": "Matéria pesada, mas a professora explica muito bem."},
        {"data": "17/04/2026", "comentario": "As listas ajudam bastante. Exige dedicação semanal."},
        {"data": "05/04/2026", "comentario": "Provas difíceis, porém coerentes com o conteúdo."},
    ]

    context = {"disciplina": disciplina, "turmas": turmas, "avaliacoes": avaliacoes}
    return render(request, "core/matricula_turma.html", context)
