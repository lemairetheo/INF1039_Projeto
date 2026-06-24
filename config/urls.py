from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('disciplinas/', views.disciplinas, name='disciplinas'),
    path('disciplinas/solicitar/', views.solicitar_disciplina, name='solicitar_disciplina'),
    path('disciplinas/<int:pk>/', views.disciplina_detalhe, name='disciplina_detalhe'),
    path('professores/', views.professores, name='professores'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login1.html', next_page='/login-redirect/'), name='login'),
    path('login-redirect/', views.login_redirect_view, name='login_redirect'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('professor/perfil/', views.professor_perfil, name='professor_perfil'),
    path('grade/', views.grade_view, name='grade'),
    path('matricula/', views.matricula_view, name='matricula'),
    path('inscrever-turma/<int:disciplina_id>/', views.inscrever_disciplina, name='inscrever_disciplina'),
    path('cancelar-turma/<int:disciplina_id>/', views.cancelar_inscricao, name='cancelar_inscricao'),
    path('erro_404/', views.erro_404, name='erro_404'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('avaliacao/nova/', views.criar_avaliacao, name='Nova Avaliação'),
    path('avaliacoes/', views.avaliacoes, name='Avaliações'),
    path('avaliacoes/reportar/<int:avaliacao_id>/', views.reportar_avaliacoes, name='Reportar Avaliação'),
    path('historico/', views.historico_grades, name='historico_grades'),
    path('progressao/', views.progressao_academica, name='progressao_academica'),
    path('minhas-avaliacoes/<int:id_professor>', views.minhas_avaliacoes_prof, name='minhas avaliações'),
    path('disciplinas/<int:pk>/', views.disciplina_detalhe, name='disciplina_detalhe'),
    path('admin-painel/', views.painel_admin, name='painel_admin'),
    path('admin-painel/aprovar/<int:sol_id>/', views.admin_aprovar_solicitacao, name='admin_aprovar_solicitacao'),
    path('admin-painel/rejeitar/<int:sol_id>/', views.admin_rejeitar_solicitacao, name='admin_rejeitar_solicitacao'),
    path('admin-painel/deletar-avaliacao/<int:avaliacao_id>/', views.admin_deletar_avaliacao, name='admin_deletar_avaliacao'),
    path('admin-painel/deletar-disciplina/<int:disciplina_id>/', views.admin_deletar_disciplina, name='admin_deletar_disciplina'),
]

handler404 = 'core.views.erro_404'
