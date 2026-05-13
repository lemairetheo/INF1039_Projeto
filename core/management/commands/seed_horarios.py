from django.core.management.base import BaseCommand
from core.models import Horario, Disciplina


HORARIOS = [
    {"disciplina": "INF1039", "dia": "2", "inicio": "08:00", "fim": "09:40"},
    {"disciplina": "INF1039", "dia": "4", "inicio": "08:00", "fim": "09:40"},
    {"disciplina": "INF1020", "dia": "3", "inicio": "10:00", "fim": "11:40"},
    {"disciplina": "INF1020", "dia": "5", "inicio": "10:00", "fim": "11:40"},
    {"disciplina": "INF1025", "dia": "2", "inicio": "13:00", "fim": "14:40"},
    {"disciplina": "INF1025", "dia": "4", "inicio": "13:00", "fim": "14:40"},
    {"disciplina": "INF1010", "dia": "3", "inicio": "08:00", "fim": "09:40"},
    {"disciplina": "INF1010", "dia": "5", "inicio": "08:00", "fim": "09:40"},
    {"disciplina": "MAT1001", "dia": "2", "inicio": "10:00", "fim": "11:40"},
    {"disciplina": "MAT1001", "dia": "6", "inicio": "10:00", "fim": "11:40"},
    {"disciplina": "INF1045", "dia": "3", "inicio": "13:00", "fim": "14:40"},
    {"disciplina": "INF1045", "dia": "5", "inicio": "13:00", "fim": "14:40"},
    {"disciplina": "INF1030", "dia": "4", "inicio": "15:00", "fim": "16:40"},
    {"disciplina": "INF1030", "dia": "6", "inicio": "15:00", "fim": "16:40"},
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com horários de exemplo'

    def handle(self, *args, **kwargs):
        created_count = 0

        for data in HORARIOS:
            disciplina = Disciplina.objects.filter(codigo=data['disciplina']).first()

            if not disciplina:
                self.stdout.write(self.style.WARNING(
                    f'  ⚠ Disciplina não encontrada: {data["disciplina"]} — rode seed_disciplinas primeiro'
                ))
                continue

            horario, created = Horario.objects.get_or_create(
                disciplina=disciplina,
                dia_semana=data['dia'],
                horario_inicio=data['inicio'],
                defaults={'horario_fim': data['fim']}
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'  ✔ {disciplina.codigo} — {horario.get_dia_semana_display()} {data["inicio"]}–{data["fim"]}'
                ))
            else:
                self.stdout.write(f'  – Já existe: {disciplina.codigo} {horario.get_dia_semana_display()}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} horário(s) criado(s) com sucesso!'))
