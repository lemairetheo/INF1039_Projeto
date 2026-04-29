from django.core.management.base import BaseCommand
from core.models import Grade, Student, Disciplina


GRADES = [
    {"matricula": "2024001", "semestre": 1, "ano": 2025, "disciplinas": ["INF1010", "MAT1001"]},
    {"matricula": "2024002", "semestre": 2, "ano": 2025, "disciplinas": ["INF1020", "INF1025"]},
    {"matricula": "2024003", "semestre": 3, "ano": 2025, "disciplinas": ["INF1039", "INF1030"]},
    {"matricula": "2024004", "semestre": 4, "ano": 2025, "disciplinas": ["INF1045", "INF1030"]},
    {"matricula": "2024005", "semestre": 1, "ano": 2025, "disciplinas": ["INF1010", "MAT1001"]},
    {"matricula": "2024006", "semestre": 2, "ano": 2025, "disciplinas": ["INF1020", "INF1025"]},
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com grades de exemplo'

    def handle(self, *args, **kwargs):
        created_count = 0

        for data in GRADES:
            student = Student.objects.filter(matricula=data['matricula']).first()

            if not student:
                self.stdout.write(self.style.WARNING(f'  ⚠ Estudante não encontrado: {data["matricula"]} — rode seed_students primeiro'))
                continue

            grade, created = Grade.objects.get_or_create(
                aluno=student,
                semestre=data['semestre'],
                ano=data['ano'],
            )

            disciplinas = Disciplina.objects.filter(
                codigo__in=data['disciplinas']
            )

            if not disciplinas.exists():
                self.stdout.write(self.style.WARNING(f'  ⚠ Nenhuma disciplina encontrada para {student}'))
                continue

            grade.disciplinas.set(disciplinas)

            if created:
                created_count += 1

                self.stdout.write(self.style.SUCCESS(f'  ✔ Grade criada para {student}'))
            else:
                self.stdout.write(f'  – Grade já existe para {student}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} grade(s) criada(s) com sucesso!'))