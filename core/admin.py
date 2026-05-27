from django.contrib import admin
from .models import Student, Professor, Disciplina, Matricula, Avaliacao, Turma


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
    list_display  = ('codigo', 'nome', 'creditos', 'periodo', 'status')
    list_filter   = ('periodo', 'status')
    search_fields = ('codigo', 'nome')
    inlines       = [TurmaInline]


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display  = ('disciplina', 'professor', 'dia_semana', 'horario')
    list_filter   = ('dia_semana', 'professor')
    search_fields = ('disciplina__nome', 'professor__nome')


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display  = ('aluno', 'disciplina', 'semestre', 'ano')
    list_filter   = ('ano', 'semestre')
    search_fields = ('aluno__user__first_name', 'disciplina__nome')


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display  = ('aluno', 'disciplina', 'nota')
    list_filter   = ('disciplina',)
    search_fields = ('aluno__user__first_name', 'disciplina__nome')
