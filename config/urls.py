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
]
