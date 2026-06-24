from django.core.management.base import BaseCommand
from core.models import Curriculo, CurriculoItem, Disciplina, Student

# ── Disciplinas necessárias ────────────────────────────────────────────────────
# (codigo, nome, creditos, periodo_modelo)
DISCIPLINAS_EXTRA = [
    # Matemática / Física
    ('MAT1002', 'Cálculo II',                        4,  2),
    ('MAT1003', 'Cálculo III',                       4,  3),
    ('MAT1004', 'Probabilidade e Estatística',        4,  4),
    ('FIS1001', 'Física I',                           4,  2),
    ('FIS1002', 'Física II',                          4,  3),
    # Ciência da Computação
    ('INF1050', 'Teoria dos Grafos',                  4,  3),
    ('INF1051', 'Linguagens Formais e Autômatos',     4,  4),
    ('INF1052', 'Compiladores',                       4,  5),
    ('INF1053', 'Sistemas Operacionais',              4,  4),
    ('INF1054', 'Arquitetura de Computadores',        4,  3),
    ('INF1055', 'Computação Paralela',                4,  6),
    ('INF1056', 'TCC I',                              4,  7),
    ('INF1057', 'TCC II',                             4,  8),
    # Engenharia
    ('ELE1001', 'Circuitos Elétricos',                4,  3),
    ('ELE1002', 'Eletrônica Digital',                 4,  4),
    ('ELE1003', 'Sistemas Embarcados',                4,  6),
    # Sistemas de Informação
    ('ADM1001', 'Introdução à Administração',         2,  1),
    ('ADM1002', 'Gestão de Projetos',                 4,  4),
    ('ADM1003', 'Empreendedorismo em TI',             2,  7),
    ('INF1060', 'Sistemas de Informação Gerencial',   4,  3),
    ('INF1061', 'Governança de TI',                   4,  5),
    ('INF1062', 'Auditoria de Sistemas',              4,  6),
    ('INF1063', 'ERP e Sistemas Integrados',          4,  5),
    ('INF1064', 'Business Intelligence',              4,  6),
    ('INF1065', 'Gestão do Conhecimento',             4,  7),
    # Optativas compartilhadas
    ('INF2100', 'Machine Learning',                   4,  6),
    ('INF2101', 'Computação em Nuvem',                4,  6),
    ('INF2102', 'Desenvolvimento Mobile',             4,  7),
    ('INF2103', 'Internet das Coisas',                4,  7),
    ('INF2104', 'Blockchain e Criptografia',          4,  8),
    ('INF2105', 'Processamento de Linguagem Natural', 4,  8),
    ('INF2106', 'Realidade Virtual e Aumentada',      4,  7),
    ('INF2107', 'Cybersegurança Avançada',            4,  8),
    ('INF2108', 'DevOps e Integração Contínua',       4,  7),
    ('INF2109', 'Análise de Dados com Python',        4,  6),
]

# ── Definição dos 3 currículos ─────────────────────────────────────────────────
CURRICULOS = [
    {
        'codigo': 'ENG-COMP',
        'nome':   'Engenharia de Computação',
        'descricao': 'Formação em hardware, software e sistemas computacionais com base sólida em matemática e física.',
        'total_creditos_obrigatorios': 188,
        'total_creditos_optativos':    24,
        'items': [
            # (codigo_disciplina, periodo, tipo)
            # ── Período 1 ──
            ('MAT1001', 1, 'obrigatoria'),
            ('INF1010', 1, 'obrigatoria'),
            ('MAT1000', 1, 'obrigatoria'),
            ('PORT3',   1, 'obrigatoria'),
            # ── Período 2 ──
            ('MAT1002', 2, 'obrigatoria'),
            ('INF1020', 2, 'obrigatoria'),
            ('FIS1001', 2, 'obrigatoria'),
            ('INF1007', 2, 'obrigatoria'),
            # ── Período 3 ──
            ('MAT1003', 3, 'obrigatoria'),
            ('INF1025', 3, 'obrigatoria'),
            ('INF1027', 3, 'obrigatoria'),
            ('FIS1002', 3, 'obrigatoria'),
            ('ELE1001', 3, 'obrigatoria'),
            # ── Período 4 ──
            ('INF1030', 4, 'obrigatoria'),
            ('INF1045', 4, 'obrigatoria'),
            ('INF1053', 4, 'obrigatoria'),
            ('INF1006', 4, 'obrigatoria'),
            ('ELE1002', 4, 'obrigatoria'),
            # ── Período 5 ──
            ('INF1039', 5, 'obrigatoria'),
            ('INF1383', 5, 'obrigatoria'),
            ('INF1318', 5, 'obrigatoria'),
            ('MAT1004', 5, 'obrigatoria'),
            # ── Período 6 ──
            ('INF1636', 6, 'obrigatoria'),
            ('INF1403', 6, 'obrigatoria'),
            ('CTC4002', 6, 'obrigatoria'),
            ('ELE1003', 6, 'obrigatoria'),
            # ── Período 7 ──
            ('INF1620', 7, 'obrigatoria'),
            ('INF1052', 7, 'obrigatoria'),
            ('INF1056', 7, 'obrigatoria'),
            # ── Período 8 ──
            ('INF1057', 8, 'obrigatoria'),
            # ── Optativas ──
            ('INF2100', 6, 'optativa'),
            ('INF2101', 6, 'optativa'),
            ('INF2102', 7, 'optativa'),
            ('INF2103', 7, 'optativa'),
            ('INF2104', 8, 'optativa'),
            ('INF2105', 8, 'optativa'),
            ('INF2106', 7, 'optativa'),
            ('INF2107', 8, 'optativa'),
        ],
    },
    {
        'codigo': 'CC',
        'nome':   'Ciência da Computação',
        'descricao': 'Formação teórica e prática em algoritmos, linguagens, sistemas e teoria da computação.',
        'total_creditos_obrigatorios': 176,
        'total_creditos_optativos':    28,
        'items': [
            # ── Período 1 ──
            ('MAT1001', 1, 'obrigatoria'),
            ('INF1010', 1, 'obrigatoria'),
            ('MAT1000', 1, 'obrigatoria'),
            ('INF1007', 1, 'obrigatoria'),
            # ── Período 2 ──
            ('MAT1002', 2, 'obrigatoria'),
            ('INF1020', 2, 'obrigatoria'),
            ('INF1054', 2, 'obrigatoria'),
            ('PORT3',   2, 'obrigatoria'),
            # ── Período 3 ──
            ('MAT1003', 3, 'obrigatoria'),
            ('INF1025', 3, 'obrigatoria'),
            ('INF1027', 3, 'obrigatoria'),
            ('INF1050', 3, 'obrigatoria'),
            # ── Período 4 ──
            ('INF1030', 4, 'obrigatoria'),
            ('INF1045', 4, 'obrigatoria'),
            ('INF1053', 4, 'obrigatoria'),
            ('INF1051', 4, 'obrigatoria'),
            ('MAT1004', 4, 'obrigatoria'),
            # ── Período 5 ──
            ('INF1039', 5, 'obrigatoria'),
            ('INF1383', 5, 'obrigatoria'),
            ('INF1052', 5, 'obrigatoria'),
            ('INF1318', 5, 'obrigatoria'),
            # ── Período 6 ──
            ('INF1620', 6, 'obrigatoria'),
            ('INF1636', 6, 'obrigatoria'),
            ('INF1055', 6, 'obrigatoria'),
            ('CTC4002', 6, 'obrigatoria'),
            # ── Período 7 ──
            ('INF1403', 7, 'obrigatoria'),
            ('INF1006', 7, 'obrigatoria'),
            ('INF1056', 7, 'obrigatoria'),
            # ── Período 8 ──
            ('INF1057', 8, 'obrigatoria'),
            # ── Optativas ──
            ('INF2100', 5, 'optativa'),
            ('INF2105', 6, 'optativa'),
            ('INF2103', 6, 'optativa'),
            ('INF2101', 7, 'optativa'),
            ('INF2102', 7, 'optativa'),
            ('INF2104', 8, 'optativa'),
            ('INF2107', 8, 'optativa'),
            ('INF2108', 7, 'optativa'),
            ('INF2109', 6, 'optativa'),
        ],
    },
    {
        'codigo': 'SI',
        'nome':   'Sistemas de Informação',
        'descricao': 'Formação voltada para a gestão e desenvolvimento de sistemas de informação nas organizações.',
        'total_creditos_obrigatorios': 164,
        'total_creditos_optativos':    32,
        'items': [
            # ── Período 1 ──
            ('MAT1001', 1, 'obrigatoria'),
            ('INF1010', 1, 'obrigatoria'),
            ('ADM1001', 1, 'obrigatoria'),
            ('PORT3',   1, 'obrigatoria'),
            # ── Período 2 ──
            ('INF1020', 2, 'obrigatoria'),
            ('INF1025', 2, 'obrigatoria'),
            ('MAT1004', 2, 'obrigatoria'),
            ('INF1007', 2, 'obrigatoria'),
            # ── Período 3 ──
            ('INF1027', 3, 'obrigatoria'),
            ('INF1060', 3, 'obrigatoria'),
            ('INF1045', 3, 'obrigatoria'),
            ('INF1006', 3, 'obrigatoria'),
            # ── Período 4 ──
            ('INF1030', 4, 'obrigatoria'),
            ('ADM1002', 4, 'obrigatoria'),
            ('INF1063', 4, 'obrigatoria'),
            ('INF1318', 4, 'obrigatoria'),
            # ── Período 5 ──
            ('INF1039', 5, 'obrigatoria'),
            ('INF1061', 5, 'obrigatoria'),
            ('INF1383', 5, 'obrigatoria'),
            ('INF1403', 5, 'obrigatoria'),
            # ── Período 6 ──
            ('INF1064', 6, 'obrigatoria'),
            ('INF1062', 6, 'obrigatoria'),
            ('CTC4002', 6, 'obrigatoria'),
            ('INF1636', 6, 'obrigatoria'),
            # ── Período 7 ──
            ('INF1065', 7, 'obrigatoria'),
            ('ADM1003', 7, 'obrigatoria'),
            ('INF1056', 7, 'obrigatoria'),
            # ── Período 8 ──
            ('INF1057', 8, 'obrigatoria'),
            # ── Optativas ──
            ('INF2100', 5, 'optativa'),
            ('INF2101', 6, 'optativa'),
            ('INF2102', 6, 'optativa'),
            ('INF2103', 7, 'optativa'),
            ('INF2104', 7, 'optativa'),
            ('INF2108', 6, 'optativa'),
            ('INF2109', 5, 'optativa'),
            ('INF2105', 7, 'optativa'),
            ('INF2106', 7, 'optativa'),
            ('INF2107', 8, 'optativa'),
        ],
    },
]

# Associa cada estudante seed a um currículo
ESTUDANTE_CURRICULO = {
    '2024001': 'ENG-COMP',  # Theo
    '2024002': 'CC',        # Jorge
    '2024003': 'SI',        # Thiago
    '2024004': 'ENG-COMP',  # Matheus
    '2024005': 'CC',        # Ana
    '2024006': 'SI',        # Lucas
}


class Command(BaseCommand):
    help = 'Cria os currículos e associa disciplinas e estudantes'

    def handle(self, *args, **kwargs):
        # 1. Cria/atualiza disciplinas extras
        for codigo, nome, creditos, periodo in DISCIPLINAS_EXTRA:
            _, created = Disciplina.objects.get_or_create(
                codigo=codigo,
                defaults={'nome': nome, 'creditos': creditos, 'periodo': periodo}
            )
            if created:
                self.stdout.write(f'  ✔ Disciplina criada: {codigo}')

        # 2. Cria os currículos e seus itens
        for cur_data in CURRICULOS:
            cur, created = Curriculo.objects.update_or_create(
                codigo=cur_data['codigo'],
                defaults={
                    'nome':    cur_data['nome'],
                    'descricao': cur_data['descricao'],
                    'total_creditos_obrigatorios': cur_data['total_creditos_obrigatorios'],
                    'total_creditos_optativos':    cur_data['total_creditos_optativos'],
                }
            )
            action = 'criado' if created else 'atualizado'
            self.stdout.write(self.style.SUCCESS(f'\n  ✔ Currículo {action}: {cur.nome}'))

            item_count = 0
            for codigo_disc, periodo, tipo in cur_data['items']:
                disc = Disciplina.objects.filter(codigo=codigo_disc).first()
                if not disc:
                    self.stdout.write(self.style.WARNING(f'    ⚠ Disciplina não encontrada: {codigo_disc}'))
                    continue
                CurriculoItem.objects.update_or_create(
                    curriculo=cur,
                    disciplina=disc,
                    defaults={'tipo': tipo, 'periodo_recomendado': periodo}
                )
                item_count += 1
            self.stdout.write(f'    → {item_count} disciplinas vinculadas')

        # 3. Associa estudantes aos currículos
        for matricula, cur_codigo in ESTUDANTE_CURRICULO.items():
            student = Student.objects.filter(matricula=matricula).first()
            cur = Curriculo.objects.filter(codigo=cur_codigo).first()
            if student and cur:
                student.curriculo = cur
                student.save()
                self.stdout.write(f'  ✔ {student} → {cur.codigo}')

        self.stdout.write(self.style.SUCCESS('\nCurrículos criados com sucesso!'))
