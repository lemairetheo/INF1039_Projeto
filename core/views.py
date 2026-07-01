from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Avg, Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from .models import (
    Disciplina, Professor, Matricula, Turma, Avaliacao, Student, 
    Denuncia, Requisito, SolicitacaoDisciplina, Curriculo, CurriculoItem, Status
)
from .forms import (
    UserEditForm, StudentEditForm, AvaliacaoForm, RegisterForm, SolicitacaoDisciplinaForm
)

def _is_admin(user):
    return user.is_authenticated and user.is_staff


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


# ── Views Públicas e Comuns ───────────────────────────────────────────────────

def home_view(request):
    search_query = request.GET.get('search', '').strip()
    todas = Disciplina.objects.prefetch_related('turma_disciplina__professor').all().order_by('codigo')
    
    if search_query:
        todas = todas.filter(
            Q(nome__icontains=search_query) | 
            Q(codigo__icontains=search_query) |
            Q(turma_disciplina__professor__nome__icontains=search_query)
        ).distinct()
        
    tem_mais = todas.count() > 15
    disciplinas_limitadas = todas[:15]
        
    return render(request, 'core/Homepage.html', {
        'disciplinas': disciplinas_limitadas,
        'search_query': search_query,
        'tem_mais': tem_mais
    })


def disciplinas(request):
    search_query = request.GET.get('search', '').strip()
    dept_query = request.GET.get('departamento', '').strip()
    
    todas = Disciplina.objects.prefetch_related('turma_disciplina__professor').all()
    
    if search_query:
        todas = todas.filter(
            Q(nome__icontains=search_query) | 
            Q(codigo__icontains=search_query) |
            Q(turma_disciplina__professor__nome__icontains=search_query)
        ).distinct()
        
    if dept_query:
        todas = todas.filter(codigo__istartswith=dept_query)
        
    paginator = Paginator(todas, 5)
    page_number = request.GET.get('page')
    disciplinas_paginadas = paginator.get_page(page_number)
        
    return render(request, 'core/disciplinas.html', {
        'disciplinas': disciplinas_paginadas,
        'search_query': search_query,
        'dept_query': dept_query
    })


def disciplina_detalhe(request, pk):
    disciplina = get_object_or_404(Disciplina.objects.prefetch_related('grupos_requisitos__disciplinas'), pk=pk)
    turmas = disciplina.turma_disciplina.select_related('professor').all()
    avaliacoes = disciplina.avaliacoes.select_related('aluno__user').all()
    alunos_count = Student.objects.filter(grades__disciplina=disciplina).distinct().count()
    return render(request, 'core/disciplina_detalhe.html', {
        'disciplina':   disciplina,
        'turmas':       turmas,
        'avaliacoes':   avaliacoes,
        'alunos_count': alunos_count,
    })


def professores(request):  
    search_query = request.GET.get('search', '').strip()
    todos = Professor.objects.prefetch_related('turma_professor__disciplina', 'avaliacoes').all()
    
    if search_query:
        todos = todos.filter(nome__icontains=search_query)
    
    paginator = Paginator(todos, 3)  
    page_number = request.GET.get('page')
    professores_paginados = paginator.get_page(page_number)
        
    return render(request, 'core/professores.html', {
        'professores': professores_paginados, 
        'search_query': search_query
    })


def avaliacoes(request):
    todas = Avaliacao.objects.all()
    paginator = Paginator(todas, 5)
    page_number = request.GET.get('page')
    avaliacoes_paginadas = paginator.get_page(page_number)
    
    return render(request, 'core/avaliacoes.html', {
        'avaliacoes': avaliacoes_paginadas
    })


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
        return redirect('avaliacoes') 
    return render(request, 'core/reportar-avaliacoes.html', {'avaliacao': avaliacao})


def erro_404(request, exception=None):
    return render(request, 'core/erro_404.html', status=404)


# ── Views Autenticadas (Alunos/Professores) ───────────────────────────────────

@login_required
def perfil(request):
    student = get_object_or_404(Student, user=request.user)
    disciplinas_aluno = Disciplina.objects.filter(matricula_disciplina__aluno=student).distinct()
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
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name  = form.cleaned_data['last_name']
            user.email      = form.cleaned_data['email']
            user.save()

            role = form.cleaned_data['role']
            if role == 'student':
                Student.objects.create(
                    user=user,
                    matricula=form.cleaned_data['matricula'],
                )
                login(request, user)
                return redirect('perfil')
            else:
                Professor.objects.create(
                    user=user,
                    nome=f"{user.first_name} {user.last_name}".strip() or user.username,
                    departamento=form.cleaned_data['departamento'],
                )
                login(request, user)
                return redirect('professor_perfil')
    else:
        form = RegisterForm()
    return render(request, 'core/cadastro1.html', {'form': form})


def login_redirect_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_staff:
        return redirect('painel_admin')
    if hasattr(request.user, 'student'):
        return redirect('perfil')
    if hasattr(request.user, 'professor'):
        return redirect('professor_perfil')
    return redirect('home')


@login_required
def professor_perfil(request):
    professor  = get_object_or_404(Professor, user=request.user)
    turmas     = professor.turma_professor.select_related('disciplina').all()
    avaliacoes = professor.avaliacoes.select_related('aluno__user', 'disciplina').all()
    nota_media = avaliacoes.aggregate(media=Avg('nota_prof'))['media'] or 0
    return render(request, 'core/professor_perfil.html', {
        'professor':  professor,
        'turmas':     turmas,
        'avaliacoes': avaliacoes,
        'nota_media': round(float(nota_media), 1),
    })


@login_required
def grade_view(request):
    student    = get_object_or_404(Student, user=request.user)
    matriculas = Matricula.objects.filter(aluno=student)
    disc_ids   = list(matriculas.values_list('disciplina_id', flat=True))
    turmas     = Turma.objects.filter(
        disciplina_id__in=disc_ids
    ).select_related('disciplina', 'professor').prefetch_related('dias_semana').order_by('horario')

    disc_com_turma_ids = turmas.values_list('disciplina_id', flat=True)
    disc_sem_turma = Disciplina.objects.filter(
        id__in=disc_ids
    ).exclude(id__in=disc_com_turma_ids)

    return render(request, 'core/grade.html', {
        'turmas':        turmas,
        'disc_sem_turma': disc_sem_turma,
        'has_matriculas': matriculas.exists(),
    })


def matricula_view(request):
    todas_disciplinas = Disciplina.objects.all()
    student           = get_object_or_404(Student, user=request.user) if request.user.is_authenticated else Student.objects.first()
    matriculas        = Matricula.objects.filter(aluno=student)
    matriculadas_ids  = list(matriculas.values_list('disciplina_id', flat=True))
    total_creditos    = (
        Disciplina.objects.filter(id__in=matriculadas_ids)
        .aggregate(total=Sum('creditos'))['total'] or 0
    )
    turmas_matriculadas = Turma.objects.filter(
        disciplina_id__in=matriculadas_ids
    ).select_related('disciplina', 'professor').order_by('horario')

    disciplinas_com_turmas = [
        (
            d,
            list({
                t.id: t for t in
                Turma.objects.filter(disciplina=d)
                    .select_related('professor')
                    .order_by('professor__nome', 'horario')
            }.values())
        )
        for d in todas_disciplinas
    ]

    context = {
        'disciplinas':                 todas_disciplinas,
        'matriculadas_ids':            matriculadas_ids,
        'total_creditos_matriculados': total_creditos,
        'turmas':                      turmas_matriculadas,
        'disciplinas_com_turmas':      disciplinas_com_turmas,
    }
    return render(request, 'core/matricula.html', context)


@login_required
def inscrever_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    student    = get_object_or_404(Student, user=request.user) if request.user.is_authenticated else Student.objects.first()

    if request.method == 'POST':
        Matricula.objects.get_or_create(
            aluno=student,
            disciplina=disciplina,
            defaults={'semestre': 1, 'ano': 2026}
        )
    next_url = request.POST.get('next') or request.GET.get('next') or 'matricula'
    return redirect(next_url)


@login_required
def cancelar_inscricao(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    student    = get_object_or_404(Student, user=request.user)
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


def minhas_avaliacoes_prof(request, id_professor):
    professor = get_object_or_404(Professor, id=id_professor)
    avaliacoes = Avaliacao.objects.filter(professor=professor)
    qtd_avaliacoes = avaliacoes.count()
    disciplinas = Disciplina.objects.filter(turma_disciplina__professor=professor).distinct()

    nota_professor = avaliacoes.aggregate(media=Avg('nota_prof'))['media'] or 0
    nota_disciplina = avaliacoes.aggregate(media=Avg('nota_disc'))['media'] or 0
        
    return render(request, 'core/minhas-avaliacoes-prof.html', {
        'disciplinas': disciplinas,
        'avaliacoes': avaliacoes,
        'qtd_avaliacoes': qtd_avaliacoes,
        'nota_professor': nota_professor,
        'nota_disciplina': nota_disciplina,
    })


@login_required
def solicitar_disciplina(request):
    if request.method == 'POST':
        form = SolicitacaoDisciplinaForm(request.POST)
        if form.is_valid():
            sol = form.save(commit=False)
            sol.solicitante = request.user
            sol.save()
            messages.success(request, 'Solicitação enviada! Aguarde a análise do administrador.')
            return redirect('disciplinas')
    else:
        form = SolicitacaoDisciplinaForm()
    return render(request, 'core/solicitar_disciplina.html', {'form': form})


@login_required
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
        }
    ]
    avaliacoes = [
        {"data": "29/04/2026", "comentario": "Matéria pesada, mas a professora explica muito bem."},
        {"data": "17/04/2026", "comentario": "As listas ajudam bastante. Exige dedicação semanal."}
    ]
    context = {"disciplina": disciplina, "turmas": turmas, "avaliacoes": avaliacoes}
    return render(request, "core/matricula_turma.html", context)


# ── Área de Controle do Administrador (Staff Only) ─────────────────────────────

@user_passes_test(_is_admin, login_url='/login/')
def painel_admin(request):
    total_matriculas = Matricula.objects.count()
    total_estudantes = Student.objects.count()
    total_denuncias  = Denuncia.objects.count()
    
    solicitacoes = SolicitacaoDisciplina.objects.filter(status='PENDENTE').select_related('solicitante')[:5]
    disciplinas_list = Disciplina.objects.all().order_by('codigo')[:5]

    context = {
        'total_matriculas': total_matriculas,
        'total_estudantes': total_estudantes,
        'total_denuncias': total_denuncias,
        'solicitacoes': solicitacoes,
        'disciplinas': disciplinas_list,
    }
    return render(request, 'core/admin.html', context)


@user_passes_test(_is_admin, login_url='/login/')
def admin_avaliacoes(request):
    todas_av = Avaliacao.objects.select_related('aluno__user', 'disciplina', 'professor').all()
    paginator = Paginator(todas_av, 10)
    page_number = request.GET.get('page')
    avaliacoes_paginadas = paginator.get_page(page_number)
    return render(request, 'core/admin_panel_avaliacoes.html', {'avaliacoes': avaliacoes_paginadas})


@user_passes_test(_is_admin, login_url='/login/')
def admin_avaliacoes_denunciadas(request):
    denuncias = Denuncia.objects.select_related('avaliacao__aluno__user', 'avaliacao__disciplina').all()
    return render(request, 'core/avaliacoes_denunciadas.html', {'denuncias': denuncias})


@user_passes_test(_is_admin, login_url='/login/')
def admin_gerenciar_disciplinas(request):
    disciplinas_list = Disciplina.objects.all().order_by('codigo')
    return render(request, 'core/admin_panel_disciplinas.html', {'disciplinas': disciplinas_list})


@user_passes_test(_is_admin, login_url='/login/')
def painel_admin_legado(request):
    solicitacoes = SolicitacaoDisciplina.objects.select_related('solicitante').all()

    av_qs = Avaliacao.objects.select_related('aluno__user', 'disciplina', 'professor')
    av_disciplina = request.GET.get('av_disciplina', '').strip()
    av_nota_min   = request.GET.get('av_nota_min', '').strip()
    av_nota_max   = request.GET.get('av_nota_max', '').strip()
    if av_disciplina:
        av_qs = av_qs.filter(disciplina__nome__icontains=av_disciplina)
    if av_nota_min:
        av_qs = av_qs.filter(nota_disc__gte=av_nota_min)
    if av_nota_max:
        av_qs = av_qs.filter(nota_disc__lte=av_nota_max)

    disc_qs     = Disciplina.objects.all()
    disc_busca  = request.GET.get('disc_busca', '').strip()
    disc_status = request.GET.get('disc_status', '').strip()
    disc_periodo = request.GET.get('disc_periodo', '').strip()
    if disc_busca:
        disc_qs = disc_qs.filter(Q(nome__icontains=disc_busca) | Q(codigo__icontains=disc_busca))
    if disc_status:
        disc_qs = disc_qs.filter(status=disc_status)
    if disc_periodo:
        disc_qs = disc_qs.filter(periodo=disc_periodo)

    av_page   = Paginator(av_qs, 10).get_page(request.GET.get('av_page'))
    disc_page = Paginator(disc_qs, 10).get_page(request.GET.get('disc_page'))

    curriculos = Curriculo.objects.prefetch_related('items').all()

    return render(request, 'core/painel_admin.html', {
        'solicitacoes':  solicitacoes,
        'av_page':       av_page,
        'disc_page':     disc_page,
        'status_choices': Status.choices if hasattr(Status, 'choices') else [],
        'periodos':      range(1, 11),
        'av_disciplina': av_disciplina,
        'av_nota_min':   av_nota_min,
        'av_nota_max':   av_nota_max,
        'disc_busca':    disc_busca,
        'disc_status':   disc_status,
        'disc_periodo':  disc_periodo,
        'curriculos':    curriculos,
    })


@user_passes_test(_is_admin, login_url='/login/')
def admin_aprovar_solicitacao(request, sol_id):
    sol = get_object_or_404(SolicitacaoDisciplina, id=sol_id)
    if request.method == 'POST':
        sol.status = SolicitacaoDisciplina.StatusSolicitacao.APROVADO
        sol.save()
        Disciplina.objects.get_or_create(
            codigo=sol.codigo,
            defaults={
                'nome':     sol.nome,
                'creditos': sol.creditos,
                'periodo':  sol.periodo,
            }
        )
        messages.success(request, f'Disciplina "{sol.nome}" aprovada e criada.')
    return redirect('painel_admin')


@user_passes_test(_is_admin, login_url='/login/')
def admin_rejeitar_solicitacao(request, sol_id):
    sol = get_object_or_404(SolicitacaoDisciplina, id=sol_id)
    if request.method == 'POST':
        sol.status = SolicitacaoDisciplina.StatusSolicitacao.REJEITADO
        sol.save()
        messages.success(request, f'Solicitação "{sol.nome}" rejeitada.')
    return redirect('painel_admin')


@user_passes_test(_is_admin, login_url='/login/')
def admin_deletar_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if request.method == 'POST':
        avaliacao.delete()
        messages.success(request, 'Avaliação removida.')
    return redirect('painel_admin')


@user_passes_test(_is_admin, login_url='/login/')
def admin_deletar_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id)
    if request.method == 'POST':
        disciplina.delete()
        messages.success(request, f'Disciplina "{disciplina.nome}" removida.')
    return redirect('painel_admin')


@user_passes_test(_is_admin, login_url='/login/')
def admin_curriculo_detalhe(request, cur_id):
    curriculo  = get_object_or_404(Curriculo, id=cur_id)
    todas_disc = Disciplina.objects.order_by('codigo')
    items      = curriculo.items.select_related('disciplina')

    f_periodo = request.GET.get('periodo', '').strip()
    f_tipo    = request.GET.get('tipo', '').strip()
    f_busca   = request.GET.get('busca', '').strip()
    f_creditos = request.GET.get('creditos', '').strip()

    if f_periodo:
        items = items.filter(periodo_recomendado=f_periodo)
    if f_tipo:
        items = items.filter(tipo=f_tipo)
    if f_busca:
        items = items.filter(Q(disciplina__nome__icontains=f_busca) | Q(disciplina__codigo__icontains=f_busca))
    if f_creditos:
        items = items.filter(disciplina__creditos=f_creditos)

    items = items.order_by('periodo_recomendado', 'tipo', 'disciplina__nome')

    return render(request, 'core/admin_curriculo.html', {
        'curriculo':    curriculo,
        'items':        items,
        'todas_disc':    todas_disc,
        'tipo_choices': CurriculoItem.Tipo.choices,
        'periodos':      range(1, 9),
        'f_periodo':    f_periodo,
        'f_tipo':       f_tipo,
        'f_busca':      f_busca,
        'f_creditos':    f_creditos,
        'total_items':  curriculo.items.count(),
    })


@user_passes_test(_is_admin, login_url='/login/')
def admin_curriculo_add_item(request, cur_id):
    curriculo = get_object_or_404(Curriculo, id=cur_id)
    if request.method == 'POST':
        disc_id = request.POST.get('disciplina')
        tipo    = request.POST.get('tipo')
        periodo = request.POST.get('periodo_recomendado')
        disc    = get_object_or_404(Disciplina, id=disc_id)
        _, created = CurriculoItem.objects.get_or_create(
            curriculo=curriculo, disciplina=disc,
            defaults={'tipo': tipo, 'periodo_recomendado': periodo}
        )
        if created:
            messages.success(request, f'"{disc.nome}" adicionada ao currículo.')
        else:
            messages.warning(request, f'"{disc.nome}" já está neste currículo.')
    return redirect('admin_curriculo_detalhe', cur_id=cur_id)


@user_passes_test(_is_admin, login_url='/login/')
def admin_curriculo_remove_item(request, item_id):
    item = get_object_or_404(CurriculoItem, id=item_id)
    cur_id = item.curriculo_id
    if request.method == 'POST':
        nome = item.disciplina.nome
        item.delete()
        messages.success(request, f'"{nome}" removida do currículo.')
    return redirect('admin_curriculo_detalhe', cur_id=cur_id)


@user_passes_test(_is_admin, login_url='/login/')
def admin_curriculo_update_item(request, item_id):
    item = get_object_or_404(CurriculoItem, id=item_id)
    cur_id = item.curriculo_id
    if request.method == 'POST':
        item.tipo               = request.POST.get('tipo', item.tipo)
        item.periodo_recomendado = int(request.POST.get('periodo_recomendado', item.periodo_recomendado))
        item.save()
        messages.success(request, f'"{item.disciplina.nome}" atualizada.')
    return redirect('admin_curriculo_detalhe', cur_id=cur_id)


@login_required
def progressao_academica(request):
    student = get_object_or_404(Student, user=request.user)
    curriculo = student.curriculo

    if not curriculo:
        return render(request, 'core/progressao.html', {'sem_curriculo': True})

    items = curriculo.items.select_related('disciplina').order_by('periodo_recomendado', 'tipo', 'disciplina__nome')
    matriculas_map = {m.disciplina_id: m for m in Matricula.objects.filter(aluno=student)}
    concluidas_ids = {did for did, m in matriculas_map.items() if m.status == Matricula.StatusMatricula.CONCLUIDO}

    periodos = {}
    stats = {'obrig_total': 0, 'obrig_ok': 0, 'optat_total': 0, 'optat_ok': 0}

    for item in items:
        p = item.periodo_recomendado
        if p not in periodos:
            periodos[p] = []

        matricula = matriculas_map.get(item.disciplina_id)
        if matricula:
            status = matricula.status
        else:
            prereqs = item.disciplina.grupos_requisitos.prefetch_related('disciplinas').filter(tipo='PRE')
            bloqueado = False
            for grupo in prereqs:
                ids = list(grupo.disciplinas.values_list('id', flat=True))
                if grupo.operador == 'AND' and not all(i in concluidas_ids for i in ids):
                    bloqueado = True
                    break
                if grupo.operador == 'OR' and not any(i in concluidas_ids for i in ids):
                    bloqueado = True
                    break
            status = 'bloqueado' if bloqueado else 'disponivel'

        periodos[p].append({
            'disciplina': item.disciplina,
            'tipo':        item.tipo,
            'status':      status,
        })

        cred = item.disciplina.creditos
        if item.tipo == CurriculoItem.Tipo.OBRIGATORIA:
            stats['obrig_total'] += cred
            if status == 'concluido':
                stats['obrig_ok'] += cred
        else:
            stats['optat_total'] += cred
            if status == 'concluido':
                stats['optat_ok'] += cred

    obrig_pct = round(stats['obrig_ok'] / stats['obrig_total'] * 100) if stats['obrig_total'] else 0
    optat_pct = round(stats['optat_ok'] / stats['optat_total'] * 100) if stats['optat_total'] else 0

    return render(request, 'core/progressao.html', {
        'student':   student,
        'curriculo': curriculo,
        'periodos':  sorted(periodos.items()),
        'stats':     stats,
        'obrig_pct': obrig_pct,
        'optat_pct': optat_pct,
    })
