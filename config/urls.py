from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('disciplinas/', views.disciplinas, name='disciplinas'),
    path('disciplinas/<int:pk>/', views.disciplina_detalhe, name='disciplina_detalhe'),
    path('professores/', views.professores, name='professores'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login1.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('grade/', views.grade_view, name='grade'),
    path('matricula/', views.matricula_view, name='matricula'),
    path('inscrever-turma/<int:disciplina_id>/', views.inscrever_disciplina, name='inscrever_disciplina'),
    path('cancelar-turma/<int:disciplina_id>/', views.cancelar_inscricao, name='cancelar_inscricao'),
    path('erro_404/', views.erro_404, name='erro_404'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('avaliacao/nova/', views.criar_avaliacao, name='Nova Avaliação'),
    path('avaliacoes/', views.avaliacoes, name='Avaliações'),
    path('avaliacoes/reportar/', views.reportar_avaliacoes, name='Reportar Avaliação'),
    path('historico/', views.historico_grades, name='historico_grades'),
    path('minhas-avaliacoes/', views.minhas_avaliacoes_prof, name='minhas avaliações'),
    path('detalhes_disciplina/', views.detalhes_disciplina, name='detalhes_disciplina'),
]

handler404 = 'core.views.erro_404'
