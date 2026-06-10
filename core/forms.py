from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student, Professor, Avaliacao, Disciplina


ROLE_CHOICES = [
    ('student',   'Estudante'),
    ('professor', 'Professor'),
]

class RegisterForm(UserCreationForm):
    first_name   = forms.CharField(max_length=50, label='Nome')
    last_name    = forms.CharField(max_length=50, label='Sobrenome')
    email        = forms.EmailField(label='Email')
    role         = forms.ChoiceField(choices=ROLE_CHOICES, label='Tipo de conta', widget=forms.RadioSelect)
    # Campos específicos por papel
    matricula    = forms.CharField(max_length=20, required=False, label='Matrícula', help_text='Obrigatório para estudantes')
    departamento = forms.CharField(max_length=100, required=False, label='Departamento', help_text='Obrigatório para professores')

    class Meta(UserCreationForm.Meta):
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        if role == 'student' and not cleaned.get('matricula'):
            self.add_error('matricula', 'A matrícula é obrigatória para estudantes.')
        if role == 'professor' and not cleaned.get('departamento'):
            self.add_error('departamento', 'O departamento é obrigatório para professores.')
        return cleaned


class UserEditForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Primeiro nome'}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Sobrenome'}),
            'email':      forms.EmailInput(attrs={'placeholder': 'seu@email.com'}),
        }
        labels = {
            'first_name': 'Nome',
            'last_name':  'Sobrenome',
            'email':      'Email',
        }


class StudentEditForm(forms.ModelForm):
    class Meta:
        model  = Student
        fields = ['bio', 'foto']
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Fale um pouco sobre você...', 'rows': 4}),
        }
        labels = {
            'bio':  'Bio',
            'foto': 'Foto de perfil',
        }


class AvaliacaoForm(forms.ModelForm):
    nota = forms.DecimalField(
        min_value=0,
        max_value=10,
        decimal_places=1,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model  = Avaliacao
        fields = ['disciplina', 'nota', 'comentario']
        widgets = {
            'disciplina': forms.Select(),
            'comentario': forms.Textarea(attrs={
                'placeholder': 'Descreva sua experiência com detalhes...',
                'rows': 4,
            }),
        }
        labels = {
            'disciplina': 'Selecione o Curso',
            'comentario': 'Comentário (opcional)',
        }

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        if student:
            # Só mostrar disciplinas em que o aluno está inscrito
            self.fields['disciplina'].queryset = Disciplina.objects.filter(
                matricula_disciplina__aluno=student
            ).distinct()
