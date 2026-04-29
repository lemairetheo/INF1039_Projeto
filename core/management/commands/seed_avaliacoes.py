from django.core.management.base import BaseCommand
from core.models import Avaliacao, Student, Disciplina


AVALIACOES = [
    {"matricula": "2024001", "disciplina": "INF1010", "nota": 8.0, "comentario": "Muito bom desempenho."},
    {"matricula": "2024001", "disciplina": "MAT1001", "nota": 7.0, "comentario": "Bom aluno, mas pode melhorar nos exercícios."},
    {"matricula": "2024002", "disciplina": "INF1020", "nota": 9.2, "comentario": "Excelente participação em aula."},
    {"matricula": "2024002", "disciplina": "INF1025", "nota": 8.0, "comentario": "Ótimo entendimento de banco de dados."},
    {"matricula": "2024003", "disciplina": "INF1039", "nota": 7.8, "comentario": "Projeto entregue corretamente."},
    {"matricula": "2024004", "disciplina": "INF1045", "nota": 6.5, "comentario": "Precisa melhorar a parte prática."},
    {"matricula": "2024005", "disciplina": "MAT1001", "nota": 9.5, "comentario": "Excelente desempenho em cálculo."},
    {"matricula": "2024006", "disciplina": "INF1025", "nota": 8.7, "comentario": "Muito bom trabalho nas atividades."},
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com avaliações de exemplo'

    def handle(self, *args, **kwargs):
        created_count = 0

        for data in AVALIACOES:
            student = Student.objects.filter(matricula=data['matricula']).first()

            if not student:
                self.stdout.write(self.style.WARNING(f'  ⚠ Estudante não encontrado: {data["matricula"]} — rode seed_students primeiro'))
                continue

            disciplina = Disciplina.objects.filter(codigo=data['disciplina']).first()

            if not disciplina:
                self.stdout.write(self.style.WARNING(f'  ⚠ Disciplina não encontrada: {data["disciplina"]} — rode seed_disciplinas primeiro'))
                continue

            avaliacao, created = Avaliacao.objects.get_or_create(
                aluno=student,
                disciplina=disciplina,
                defaults={
                    'nota': data['nota'],
                    'comentario': data['comentario'],
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✔ Avaliação criada: {student} — {disciplina.codigo} ({data["nota"]})'))
            else:
                self.stdout.write(f'  – Avaliação já existe: {student} — {disciplina.codigo}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} avaliação(ões) criada(s) com sucesso!'))