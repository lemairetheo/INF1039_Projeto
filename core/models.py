from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

# ── Usuario (Aluno) ────────────────────────────────────────────────────────────
class Student(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    matricula  = models.CharField(max_length=20, unique=True)
    bio        = models.TextField(blank=True, null=True)
    foto       = models.ImageField(upload_to='students/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.matricula})"

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['user__last_name']


# ── Professor ──────────────────────────────────────────────────────────────────
class Professor(models.Model):
    nome         = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} ({self.departamento})"

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'
        ordering = ['nome']


# ── Disciplina ─────────────────────────────────────────────────────────────────
class Disciplina(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=100)
    creditos = models.PositiveIntegerField()
    periodo = models.PositiveIntegerField()
    professor = models.ForeignKey('Professor', on_delete=models.CASCADE, related_name='disciplinas')
    quantidade_turmas = models.PositiveIntegerField(default=1)

    @property
    def nota_media(self):
        media = self.avaliacoes.aggregate(Avg('nota'))['nota__avg']
        if media is None:
            return 0.0
        return round(float(media), 1)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

# ── Horario ─────────────────────────────────────────────────────────────────
class Horario(models.Model):
    DIAS_CHOICES = [
        ('2', 'Segunda'), ('3', 'Terça'), ('4', 'Quarta'), ('5', 'Quinta'), ('6', 'Sexta'),
    ]
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.CharField(max_length=1, choices=DIAS_CHOICES)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    def __str__(self):
        return f"{self.disciplina.nome} - {self.get_dia_semana_display()} às {self.horario_inicio}"


# ── Grade (horário semestral do aluno) ─────────────────────────────────────────
class Grade(models.Model):
    aluno       = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    semestre    = models.PositiveIntegerField()
    ano         = models.PositiveIntegerField()
    disciplinas = models.ManyToManyField(Disciplina, blank=True, related_name='grades')

    def __str__(self):
        return f"{self.aluno} — {self.semestre}º sem. {self.ano}"

    class Meta:
        verbose_name = 'Grade'
        verbose_name_plural = 'Grades'
        ordering = ['-ano', '-semestre']


# ── Avaliação ──────────────────────────────────────────────────────────────────
class Avaliacao(models.Model):
    aluno      = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='avaliacoes')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='avaliacoes')
    nota       = models.DecimalField(max_digits=4, decimal_places=2)
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.aluno} | {self.disciplina} | {self.nota}"

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['disciplina', 'aluno']
