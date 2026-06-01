from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class DiaSemana(models.TextChoices):
    SEGUNDA = "SEG", "Segunda-feira"
    TERCA = "TER", "Terça-feira"
    QUARTA = "QUA", "Quarta-feira"
    QUINTA = "QUI", "Quinta-feira"
    SEXTA = "SEX", "Sexta-feira"
    SABADO = "SAB", "Sábado"

class Horario(models.TextChoices):
    H07_09 = "07-09", "07:00 - 09:00"
    H09_11 = "09-11", "09:00 - 11:00"
    H11_13 = "11-13", "11:00 - 13:00"
    H13_15 = "13-15", "13:00 - 15:00"
    H15_17 = "15-17", "15:00 - 17:00"
    H17_19 = "17-19", "17:00 - 19:00"
    H19_21 = "19-21", "19:00 - 21:00"
 
class Status(models.TextChoices):
    APROVADO = "aprovado"
    CANCELADO = "cancelado"
    SOB_AVALIACAO = "Sob avaliaçao"


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
    quantidade_turmas = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SOB_AVALIACAO)

    @property
    def nota_media(self):
        media = self.avaliacoes.aggregate(Avg('nota'))['nota__avg']
        if media is None:
            return 0.0
        return round(float(media), 1)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class Matricula(models.Model):
    aluno       = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    disciplina  = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='matricula_disciplina')
    semestre    = models.PositiveIntegerField()
    ano         = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.aluno} — {self.semestre}º sem. {self.ano}"

    class Meta:
        verbose_name = 'Matricula'
        verbose_name_plural = 'Matriculas'
        ordering = ['-ano', '-semestre']

# ── Avaliação ──────────────────────────────────────────────────────────────────
class Avaliacao(models.Model):
    aluno      = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='avaliacoes')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='avaliacoes', null=True)
    professor  = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='avaliacoes', null=True)
    nota       = models.DecimalField(max_digits=4, decimal_places=2)
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.aluno} | {self.disciplina} | {self.nota}"

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['disciplina', 'aluno']


# ── Denuncia ──────────────────────────────────────────────────────────────────
class Denuncia(models.Model):
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name='denuncias')
    motivo = models.CharField(max_length=50)
    descricao = models.TextField(blank=True, null=True)
    data_denuncia = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Denúncia ({self.motivo}) - Avaliação ID: {self.avaliacao.id}"


# ── Turma ──────────────────────────────────────────────────────────────────
class Turma(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='turma_disciplina')
    professor = models.ForeignKey('Professor', on_delete=models.CASCADE, related_name='turma_professor')
    horario = models.CharField(max_length=5,choices=Horario.choices)
    dia_semana = models.CharField(max_length=3,choices=DiaSemana.choices)


    