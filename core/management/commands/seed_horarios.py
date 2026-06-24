from django.core.management.base import BaseCommand
from core.models import Turma, DiaSemanaAula, Disciplina, Professor, DiaSemana


# Chaque entrée = une turma avec potentiellement plusieurs jours
TURMAS = [
    # ── Existentes ──
    {"disciplina": "INF1039", "professor": "Ana Lima",        "horario": "09-11", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1020", "professor": "Carlos Souza",    "horario": "11-13", "dias": ["TER", "QUI"]},
    {"disciplina": "INF1025", "professor": "Maria Santos",    "horario": "13-15", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1010", "professor": "Pedro Alves",     "horario": "07-09", "dias": ["TER", "QUI"]},
    {"disciplina": "MAT1001", "professor": "Sofia Ribeiro",   "horario": "11-13", "dias": ["SEG", "SAB"]},
    {"disciplina": "INF1045", "professor": "Lucas Ferreira",  "horario": "13-15", "dias": ["TER", "QUI"]},
    {"disciplina": "INF1030", "professor": "Beatriz Costa",   "horario": "15-17", "dias": ["QUA", "SAB"]},
    # ── Matemática / Física ──
    {"disciplina": "MAT1000", "professor": "Roberto Farias",  "horario": "07-09", "dias": ["SEG", "QUA"]},
    {"disciplina": "MAT1002", "professor": "Sofia Ribeiro",   "horario": "13-15", "dias": ["TER", "QUI"]},
    {"disciplina": "MAT1003", "professor": "Roberto Farias",  "horario": "15-17", "dias": ["SEG", "QUA"]},
    {"disciplina": "MAT1004", "professor": "Sofia Ribeiro",   "horario": "09-11", "dias": ["TER", "QUI"]},
    {"disciplina": "FIS1001", "professor": "Paula Gomes",     "horario": "07-09", "dias": ["TER", "QUI"]},
    {"disciplina": "FIS1002", "professor": "Paula Gomes",     "horario": "09-11", "dias": ["SEG", "QUA"]},
    # ── Infraestrutura / Sistemas ──
    {"disciplina": "INF1053", "professor": "Marcos Alves",    "horario": "15-17", "dias": ["TER", "QUI"]},
    {"disciplina": "INF1006", "professor": "Carlos Mendes",   "horario": "17-19", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1054", "professor": "Carlos Mendes",   "horario": "07-09", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1620", "professor": "Marcos Alves",    "horario": "17-19", "dias": ["TER", "QUI"]},
    # ── Algoritmos / Teoria ──
    {"disciplina": "INF1027", "professor": "Pedro Alves",     "horario": "11-13", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1050", "professor": "Ana Lima",        "horario": "13-15", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1051", "professor": "Ana Lima",        "horario": "15-17", "dias": ["TER", "QUI"]},
    {"disciplina": "INF1052", "professor": "Carlos Souza",    "horario": "17-19", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1055", "professor": "Pedro Alves",     "horario": "19-21", "dias": ["TER", "QUI"]},
    # ── Engenharia / Hardware ──
    {"disciplina": "ELE1001", "professor": "Paula Gomes",     "horario": "11-13", "dias": ["TER", "QUI"]},
    {"disciplina": "ELE1002", "professor": "Paula Gomes",     "horario": "13-15", "dias": ["SEG", "QUA"]},
    {"disciplina": "ELE1003", "professor": "Roberto Farias",  "horario": "15-17", "dias": ["SEG", "QUA"]},
    # ── IA / Software ──
    {"disciplina": "INF1383", "professor": "Ana Lima",        "horario": "09-11", "dias": ["TER", "QUI"]},
    {"disciplina": "INF1318", "professor": "Marcos Alves",    "horario": "11-13", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1636", "professor": "Beatriz Costa",   "horario": "13-15", "dias": ["TER", "QUI"]},
    {"disciplina": "INF1403", "professor": "Ana Lima",        "horario": "07-09", "dias": ["SEG", "QUA"]},
    # ── Sistemas de Informação ──
    {"disciplina": "INF1060", "professor": "Maria Santos",    "horario": "09-11", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1061", "professor": "Carlos Mendes",   "horario": "11-13", "dias": ["TER", "QUI"]},
    {"disciplina": "INF1062", "professor": "Maria Santos",    "horario": "13-15", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1063", "professor": "Carlos Souza",    "horario": "15-17", "dias": ["TER", "QUI"]},
    {"disciplina": "INF1064", "professor": "Maria Santos",    "horario": "17-19", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF1065", "professor": "Carlos Mendes",   "horario": "09-11", "dias": ["SEG", "QUA"]},
    # ── Administração ──
    {"disciplina": "ADM1001", "professor": "Roberto Farias",  "horario": "19-21", "dias": ["SEG", "QUA"]},
    {"disciplina": "ADM1002", "professor": "Roberto Farias",  "horario": "19-21", "dias": ["TER", "QUI"]},
    {"disciplina": "ADM1003", "professor": "Paula Gomes",     "horario": "19-21", "dias": ["SEG", "QUA"]},
    # ── Optativas ──
    {"disciplina": "INF2100", "professor": "Ana Lima",        "horario": "17-19", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF2101", "professor": "Marcos Alves",    "horario": "19-21", "dias": ["TER", "QUI"]},
    {"disciplina": "INF2102", "professor": "Beatriz Costa",   "horario": "17-19", "dias": ["TER", "QUI"]},
    {"disciplina": "INF2103", "professor": "Carlos Mendes",   "horario": "19-21", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF2104", "professor": "Ana Lima",        "horario": "15-17", "dias": ["SEG", "SAB"]},
    {"disciplina": "INF2105", "professor": "Pedro Alves",     "horario": "17-19", "dias": ["QUA", "SAB"]},
    {"disciplina": "INF2106", "professor": "Beatriz Costa",   "horario": "19-21", "dias": ["SEG", "QUA"]},
    {"disciplina": "INF2107", "professor": "Marcos Alves",    "horario": "15-17", "dias": ["TER", "QUI"]},
    {"disciplina": "INF2108", "professor": "Carlos Souza",    "horario": "13-15", "dias": ["SAB"]},
    {"disciplina": "INF2109", "professor": "Maria Santos",    "horario": "11-13", "dias": ["SAB"]},
    # ── Humanidades ──
    {"disciplina": "PORT3",   "professor": "Paula Gomes",     "horario": "19-21", "dias": ["SEG"]},
    {"disciplina": "CTC4002", "professor": "Roberto Farias",  "horario": "19-21", "dias": ["QUA"]},
    {"disciplina": "INF1007", "professor": "Carlos Mendes",   "horario": "19-21", "dias": ["SEX"]},
    # ── TCC ──
    {"disciplina": "INF1056", "professor": "Ana Lima",        "horario": "09-11", "dias": ["SAB"]},
    {"disciplina": "INF1057", "professor": "Ana Lima",        "horario": "11-13", "dias": ["SAB"]},
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
