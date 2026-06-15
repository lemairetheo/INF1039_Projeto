from django.contrib import admin
from .models import Student, Professor, Disciplina, Matricula, Avaliacao, Turma, Denuncia, Requisito, DiaSemanaAula


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ('matricula', 'get_full_name', 'get_email')
    search_fields = ('matricula', 'user__first_name', 'user__last_name', 'user__email')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Nome'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display  = ('nome', 'departamento')
    search_fields = ('nome', 'departamento')


class TurmaInline(admin.TabularInline):
    model = Turma
    extra = 1


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display  = ('codigo', 'nome', 'creditos', 'periodo', 'status', 'ementa')
    list_filter   = ('periodo', 'status')
    search_fields = ('codigo', 'nome', 'ementa')
    inlines       = [TurmaInline]

@admin.register(Requisito)
class RequisitoAdmin(admin.ModelAdmin):
    list_display      = ('disciplina_principal', 'tipo', 'operador')
    list_filter       = ('tipo', 'operador')
    search_fields     = ('disciplina_principal__codigo', 'disciplina_principal__nome')
    filter_horizontal = ('disciplinas',)


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display  = ('disciplina', 'professor', 'horario', 'get_dias')
    list_filter   = ('professor',)
    search_fields = ('disciplina__nome', 'professor__nome')
    filter_horizontal = ('dias_semana',)

    def get_dias(self, obj):
        return obj.get_dias_display()
    get_dias.short_description = 'Dias'


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display  = ('aluno', 'disciplina', 'semestre', 'ano')
    list_filter   = ('ano', 'semestre')
    search_fields = ('aluno__user__first_name', 'disciplina__nome')


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display  = ('aluno', 'disciplina', 'nota_prof', 'nota_disc')
    list_filter   = ('disciplina',)
    search_fields = ('aluno__user__first_name', 'disciplina__nome')


@admin.register(DiaSemanaAula)
class DiaSemanaAulaAdmin(admin.ModelAdmin):
    list_display = ('dia', '__str__')
    ordering = ('dia',)


@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'avaliacao', 'motivo')
    list_filter  = ('motivo',)
    search_fields = ('descricao', 'motivo')