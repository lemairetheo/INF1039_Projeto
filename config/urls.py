from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home_view, name="home"),
    path("disciplinas/", views.disciplinas, name="disciplinas"),
    path(
        "disciplinas/solicitar/",
        views.solicitar_disciplina,
        name="solicitar_disciplina",
    ),
    path("disciplinas/<int:pk>/", views.disciplina_detalhe, name="disciplina_detalhe"),
    path("professores/", views.professores, name="professores"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="core/login1.html", next_page="/login-redirect/"
        ),
        name="login",
    ),
    path("login-redirect/", views.login_redirect_view, name="login_redirect"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register_view, name="register"),
    path("professor/perfil/", views.professor_perfil, name="professor_perfil"),
    path("grade/", views.grade_view, name="grade"),
    path("matricula/", views.matricula_view, name="matricula"),
    path(
        "inscrever-turma/<int:disciplina_id>/",
        views.inscrever_disciplina,
        name="inscrever_disciplina",
    ),
    path(
        "cancelar-turma/<int:disciplina_id>/",
        views.cancelar_inscricao,
        name="cancelar_inscricao",
    ),
    path("erro_404/", views.erro_404, name="erro_404"),
    path("perfil/", views.perfil, name="perfil"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("avaliacao/nova/", views.criar_avaliacao, name="Nova Avaliação"),
    path("avaliacoes/", views.avaliacoes, name="Avaliações"),
    path(
        "avaliacoes/reportar/<int:avaliacao_id>/",
        views.reportar_avaliacoes,
        name="Reportar Avaliação",
    ),
    path("historico/", views.historico_grades, name="historico_grades"),
    path("progressao/", views.progressao_academica, name="progressao_academica"),
    path(
        "minhas-avaliacoes/<int:id_professor>",
        views.minhas_avaliacoes_prof,
        name="minhas avaliações",
    ),
    path("disciplinas/<int:pk>/", views.disciplina_detalhe, name="disciplina_detalhe"),
    path("admin-painel/", views.painel_admin, name="painel_admin"),
    path(
        "admin-painel/aprovar/<int:sol_id>/",
        views.admin_aprovar_solicitacao,
        name="admin_aprovar_solicitacao",
    ),
    path(
        "admin-painel/rejeitar/<int:sol_id>/",
        views.admin_rejeitar_solicitacao,
        name="admin_rejeitar_solicitacao",
    ),
    path(
        "admin-painel/deletar-avaliacao/<int:avaliacao_id>/",
        views.admin_deletar_avaliacao,
        name="admin_deletar_avaliacao",
    ),
    path(
        "admin-painel/deletar-disciplina/<int:disciplina_id>/",
        views.admin_deletar_disciplina,
        name="admin_deletar_disciplina",
    ),
    path(
        "admin-painel/curriculos/<int:cur_id>/",
        views.admin_curriculo_detalhe,
        name="admin_curriculo_detalhe",
    ),
    path(
        "admin-painel/curriculos/<int:cur_id>/add/",
        views.admin_curriculo_add_item,
        name="admin_curriculo_add_item",
    ),
    path(
        "admin-painel/curriculos/item/<int:item_id>/remover/",
        views.admin_curriculo_remove_item,
        name="admin_curriculo_remove_item",
    ),
    path(
        "admin-painel/curriculos/item/<int:item_id>/editar/",
        views.admin_curriculo_update_item,
        name="admin_curriculo_update_item",
    ),
    # Admin Pages - Superuser only
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-avaliacoes/", views.admin_avaliacoes, name="admin_avaliacoes"),
    path(
        "admin-avaliacoes/<int:denuncia_id>/aprovar/",
        views.admin_avaliacao_aprovar,
        name="admin_avaliacao_aprovar",
    ),
    path(
        "admin-avaliacoes/<int:denuncia_id>/rejeitar/",
        views.admin_avaliacao_rejeitar,
        name="admin_avaliacao_rejeitar",
    ),
    path("admin-disciplinas/", views.admin_disciplinas, name="admin_disciplinas"),
    path(
        "admin-disciplinas/<int:disciplina_id>/aprovar/",
        views.admin_aprovar_disciplina_geral,
        name="admin_aprovar_disciplina_geral",
    ),
    path(
        "admin-disciplinas/<int:disciplina_id>/remover/",
        views.admin_remover_disciplina_geral,
        name="admin_remover_disciplina_geral",
    ),
    # Validação de Disciplinas
    path(
        "admin-validar-disciplinas/",
        views.admin_validar_disciplinas,
        name="admin_validar_disciplinas",
    ),
    path(
        "admin-validar-disciplinas/<int:disciplina_id>/aprovar/",
        views.admin_aprovar_disciplina,
        name="admin_aprovar_disciplina",
    ),
    path(
        "admin-validar-disciplinas/<int:disciplina_id>/rejeitar/",
        views.admin_rejeitar_disciplina,
        name="admin_rejeitar_disciplina",
    ),
    # Denúncias de Disciplinas
    path(
        "admin-denuncias-disciplinas/",
        views.admin_denuncias_disciplinas,
        name="admin_denuncias_disciplinas",
    ),
    path(
        "admin-denuncias-disciplinas/<int:denuncia_id>/validar/",
        views.admin_validar_denuncia_disciplina,
        name="admin_validar_denuncia_disciplina",
    ),
    path(
        "admin-denuncias-disciplinas/<int:denuncia_id>/rejeitar/",
        views.admin_rejeitar_denuncia_disciplina,
        name="admin_rejeitar_denuncia_disciplina",
    ),
    # Validação de Professores
    path(
        "admin-validar-professores/",
        views.admin_validar_professores,
        name="admin_validar_professores",
    ),
    path(
        "admin-validar-professores/<int:professor_id>/aprovar/",
        views.admin_aprovar_professor,
        name="admin_aprovar_professor",
    ),
    path(
        "admin-validar-professores/<int:professor_id>/rejeitar/",
        views.admin_rejeitar_professor,
        name="admin_rejeitar_professor",
    ),
]

handler404 = "core.views.erro_404"
