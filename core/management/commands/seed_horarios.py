from django.core.management.base import BaseCommand
from core.models import Turma, DiaSemanaAula, Disciplina, Professor, DiaSemana


# Chaque entrée = une turma avec potentiellement plusieurs jours
TURMAS = [
    {"disciplina": "INF1039", "professor": "Ana Lima",       "horario": "09-11", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1020", "professor": "Carlos Souza",   "horario": "11-13", "dias": ["TER", "QUI"]},
    {"disciplina": "INF1025", "professor": "Maria Santos",   "horario": "13-15", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1010", "professor": "Pedro Alves",    "horario": "07-09", "dias": ["TER", "QUI"]},
    {"disciplina": "MAT1001", "professor": "Sofia Ribeiro",  "horario": "11-13", "dias": ["SEG", "SAB"]},
    {"disciplina": "INF1045", "professor": "Lucas Ferreira", "horario": "13-15", "dias": ["TER", "QUI"]},
    {"disciplina": "INF1030", "professor": "Beatriz Costa",  "horario": "15-17", "dias": ["QUA", "SAB"]},
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com turmas e dias da semana'

    def handle(self, *args, **kwargs):
        # Garante que todos os dias existem
        for codigo, _ in DiaSemana.choices:
            DiaSemanaAula.objects.get_or_create(dia=codigo)
        self.stdout.write('  ✔ Dias da semana criados/verificados')

        created_count = 0

        for data in TURMAS:
            disciplina = Disciplina.objects.filter(codigo=data['disciplina']).first()
            if not disciplina:
                self.stdout.write(self.style.WARNING(
                    f'  ⚠ Disciplina não encontrada: {data["disciplina"]}'
                ))
                continue

            professor = Professor.objects.filter(nome__icontains=data['professor']).first()
            if not professor:
                dept = data['disciplina'][:3]
                professor = Professor.objects.create(nome=data['professor'], departamento=dept)
                self.stdout.write(self.style.WARNING(f'  ➕ Professor criado: {professor.nome}'))

            turma, created = Turma.objects.get_or_create(
                disciplina=disciplina,
                professor=professor,
                horario=data['horario'],
            )

            dias_objs = DiaSemanaAula.objects.filter(dia__in=data['dias'])
            turma.dias_semana.set(dias_objs)

            if created:
                created_count += 1
                dias_str = ', '.join(data['dias'])
                self.stdout.write(self.style.SUCCESS(
                    f'  ✔ Turma criada: {disciplina.codigo} — {data["horario"]} ({dias_str})'
                ))
            else:
                self.stdout.write(f'  – Já existe: {disciplina.codigo} {data["horario"]}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} turma(s) criada(s) com sucesso!'))
