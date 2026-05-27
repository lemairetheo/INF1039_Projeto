from django.core.management.base import BaseCommand
from core.models import Turma, Disciplina, Professor


# dia_semana uses DiaSemana choices: SEG, TER, QUA, QUI, SEX, SAB
# horario uses Horario choices: 07-09, 09-11, 11-13, 13-15, 15-17, 17-19, 19-21
TURMAS = [
    {"disciplina": "INF1039", "professor": "Ana Lima",        "dia": "SEG", "horario": "09-11"},
    {"disciplina": "INF1039", "professor": "Ana Lima",        "dia": "QUA", "horario": "09-11"},
    {"disciplina": "INF1020", "professor": "Carlos Souza",    "dia": "TER", "horario": "11-13"},
    {"disciplina": "INF1020", "professor": "Carlos Souza",    "dia": "QUI", "horario": "11-13"},
    {"disciplina": "INF1025", "professor": "Maria Santos",    "dia": "SEG", "horario": "13-15"},
    {"disciplina": "INF1025", "professor": "Maria Santos",    "dia": "QUA", "horario": "13-15"},
    {"disciplina": "INF1010", "professor": "Pedro Alves",     "dia": "TER", "horario": "07-09"},
    {"disciplina": "INF1010", "professor": "Pedro Alves",     "dia": "QUI", "horario": "07-09"},
    {"disciplina": "MAT1001", "professor": "Sofia Ribeiro",   "dia": "SEG", "horario": "11-13"},
    {"disciplina": "MAT1001", "professor": "Sofia Ribeiro",   "dia": "SAB", "horario": "11-13"},
    {"disciplina": "INF1045", "professor": "Lucas Ferreira",  "dia": "TER", "horario": "13-15"},
    {"disciplina": "INF1045", "professor": "Lucas Ferreira",  "dia": "QUI", "horario": "13-15"},
    {"disciplina": "INF1030", "professor": "Beatriz Costa",   "dia": "QUA", "horario": "15-17"},
    {"disciplina": "INF1030", "professor": "Beatriz Costa",   "dia": "SAB", "horario": "15-17"},
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com turmas (horários) de exemplo'

    def handle(self, *args, **kwargs):
        created_count = 0

        for data in TURMAS:
            disciplina = Disciplina.objects.filter(codigo=data['disciplina']).first()
            if not disciplina:
                self.stdout.write(self.style.WARNING(
                    f'  ⚠ Disciplina não encontrada: {data["disciplina"]} — rode seed_disciplinas primeiro'
                ))
                continue

            professor = Professor.objects.filter(nome__icontains=data['professor']).first()
            if not professor:
                # Create professor on the fly if not found
                nome_parts = data['professor'].split()
                dept = disciplina.codigo[:3]
                professor = Professor.objects.create(nome=data['professor'], departamento=dept)
                self.stdout.write(self.style.WARNING(
                    f'  ➕ Professor criado: {professor.nome} ({professor.departamento})'
                ))

            turma, created = Turma.objects.get_or_create(
                disciplina=disciplina,
                professor=professor,
                dia_semana=data['dia'],
                horario=data['horario'],
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'  ✔ Turma criada: {disciplina.codigo} — {data["dia"]} {data["horario"]} ({professor.nome})'
                ))
            else:
                self.stdout.write(f'  – Já existe: {disciplina.codigo} {data["dia"]} {data["horario"]}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} turma(s) criada(s) com sucesso!'))
