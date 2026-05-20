from django import forms
from django.contrib.auth.models import User
from .models import Student, Avaliacao, Disciplina


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
                grades__aluno=student
            ).distinct()
