from django.db import models
from django.contrib.auth.models import User


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
    codigo    = models.CharField(max_length=20, unique=True)
    nome      = models.CharField(max_length=100)
    creditos  = models.PositiveIntegerField()
    periodo   = models.PositiveIntegerField()
    professor = models.ForeignKey(
        Professor,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='disciplinas'
    )

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    class Meta:
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        ordering = ['periodo', 'nome']


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
