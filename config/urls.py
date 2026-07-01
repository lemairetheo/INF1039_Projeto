from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin nativo do Django
    path('admin/', admin.site.urls),
    
    # Homepage e Autenticação
    path('', views.home_view, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login1.html', next_page='/login-redirect/'), name='login'),
    path('login-redirect/', views.login_redirect_view, name='login_redirect'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Disciplinas (Ordem correta: estática antes da dinâmica)
    path('disciplinas/', views.disciplinas, name='disciplinas'),
    path('disciplinas/solicitar/', views.solicitar_disciplina, name='solicitar_disciplina'),
    path('disciplinas/<int:pk>/', views.disciplina_detalhe, name='disciplina_detalhe'),
    
    # Matrículas e Grade
    path('grade/', views.grade_view, name='grade'),
    path('matricula/', views.matricula_view, name='matricula'),
    path('inscrever-turma/<int:disciplina_id>/', views.inscrever_disciplina, name='inscrever_disciplina'),
    path('cancelar-turma/<int:disciplina_id>/', views.cancelar_inscricao, name='cancelar_inscricao'),
    path('historico/', views.historico_grades, name='historico_grades'),
    path('progressao/', views.progressao_academica, name='progressao_academica'),
    
    # Professores e Perfis
    path('professores/', views.professores, name='professores'),
    path('professor/perfil/', views.professor_perfil, name='professor_perfil'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    
    # Avaliações (Nomes padronizados em snake_case)
    path('avaliacao/nova/', views.criar_avaliacao, name='nova_avaliacao'),
    path('avaliacoes/', views.avaliacoes, name='avaliacoes'),
    path('avaliacoes/reportar/<int:avaliacao_id>/', views.reportar_avaliacoes, name='reportar_avaliacao'),
    path('minhas-avaliacoes/<int:id_professor>', views.minhas_avaliacoes_prof, name='minhas_avaliacoes'),
    
    # Painel Administrativo Customizado (Academic Curator)
    path('admin-painel/', views.painel_admin, name='painel_admin'),
    path('admin-painel/aprovar/<int:sol_id>/', views.admin_aprovar_solicitacao, name='admin_aprovar_solicitacao'),
    path('admin-painel/rejeitar/<int:sol_id>/', views.admin_rejeitar_solicitacao, name='admin_rejeitar_solicitacao'),
    path('admin-painel/deletar-avaliacao/<int:avaliacao_id>/', views.admin_deletar_avaliacao, name='admin_deletar_avaliacao'),
    path('admin-painel/deletar-disciplina/<int:disciplina_id>/', views.admin_deletar_disciplina, name='admin_deletar_disciplina'),
    
    # Gerenciamento de Currículos no Painel Admin
    path('admin-painel/curriculos/<int:cur_id>/', views.admin_curriculo_detalhe, name='admin_curriculo_detalhe'),
    path('admin-painel/curriculos/<int:cur_id>/add/', views.admin_curriculo_add_item, name='admin_curriculo_add_item'),
    path('admin-painel/curriculos/item/<int:item_id>/remover/', views.admin_curriculo_remove_item, name='admin_curriculo_remove_item'),
    path('admin-painel/curriculos/item/<int:item_id>/editar/', views.admin_curriculo_update_item, name='admin_curriculo_update_item'),
    
    # Páginas de Erro
    path('erro_404/', views.erro_404, name='erro_404'),
]

# Handler para erro 404 global
handler404 = 'core.views.erro_404'
