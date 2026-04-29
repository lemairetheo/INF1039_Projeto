from django.contrib import admin
from .models import Student, Professor, Disciplina, Grade, Avaliacao


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


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display  = ('codigo', 'nome', 'creditos', 'periodo', 'professor')
    list_filter   = ('periodo', 'professor')
    search_fields = ('codigo', 'nome')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display  = ('aluno', 'semestre', 'ano')
    list_filter   = ('ano', 'semestre')
    filter_horizontal = ('disciplinas',)


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display  = ('aluno', 'disciplina', 'nota')
    list_filter   = ('disciplina',)
    search_fields = ('aluno__user__first_name', 'disciplina__nome')
