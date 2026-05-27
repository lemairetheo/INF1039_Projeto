from django.core.management.base import BaseCommand
from core.models import Matricula, Student, Disciplina


MATRICULAS = [
    {"matricula": "2024001", "semestre": 1, "ano": 2025, "disciplinas": ["INF1010", "MAT1001"]},
    {"matricula": "2024002", "semestre": 2, "ano": 2025, "disciplinas": ["INF1020", "INF1025"]},
    {"matricula": "2024003", "semestre": 3, "ano": 2025, "disciplinas": ["INF1039", "INF1030"]},
    {"matricula": "2024004", "semestre": 4, "ano": 2025, "disciplinas": ["INF1045", "INF1030"]},
    {"matricula": "2024005", "semestre": 1, "ano": 2025, "disciplinas": ["INF1010", "MAT1001"]},
    {"matricula": "2024006", "semestre": 2, "ano": 2025, "disciplinas": ["INF1020", "INF1025"]},
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com matrículas de exemplo'

    def handle(self, *args, **kwargs):
        created_count = 0

        for data in MATRICULAS:
            student = Student.objects.filter(matricula=data['matricula']).first()
            if not student:
                self.stdout.write(self.style.WARNING(
                    f'  ⚠ Estudante não encontrado: {data["matricula"]} — rode seed_students primeiro'
                ))
                continue

            for codigo in data['disciplinas']:
                disciplina = Disciplina.objects.filter(codigo=codigo).first()
                if not disciplina:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠ Disciplina não encontrada: {codigo} — rode seed_disciplinas primeiro'
                    ))
                    continue

                _, created = Matricula.objects.get_or_create(
                    aluno=student,
                    disciplina=disciplina,
                    semestre=data['semestre'],
                    ano=data['ano'],
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✔ Matrícula criada: {student} → {disciplina.codigo}'
                    ))
                else:
                    self.stdout.write(f'  – Já existe: {student} → {disciplina.codigo}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} matrícula(s) criada(s) com sucesso!'))
