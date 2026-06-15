from django.core.management.base import BaseCommand
from core.models import Disciplina, Requisito

class Command(BaseCommand):
    help = 'Popula o banco com disciplinas, ementas e requisitos'

    def get_disc(self, codigo, nome_padrao=""):
        disciplina, created = Disciplina.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nome': nome_padrao or f"Disciplina Auxiliar ({codigo})", 
                'creditos': 4, 
                'periodo': 1
            }
        )
        if codigo not in self.logged_codes:
            self.logged_codes.add(codigo)
            if created:
                self.created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✔ Criado: {disciplina.nome} ({codigo})'))
            else:
                self.stdout.write(f'  – Já existe: {disciplina.nome} ({codigo})')
        return disciplina

    def handle(self, *args, **kwargs):
        self.created_count = 0
        self.logged_codes = set()

        Requisito.objects.all().delete()

        DISCIPLINAS = [
            {
                "codigo": "INF1030", "nome": "Engenharia de Software", "creditos": 4, "periodo": 3, 
                "ementa": "Funcionamento básico da Web; servidores Web (Apache, IIS); clientes; protocolo http; Introdução a HTML, XHTML e CSS; Javascript: variáveis; operadores; comandos; desvios condicionais; repetições; funções intrínsecas e do usuário; eventos; objetos básicos."
            },
            {
                "codigo": "INF1045", "nome": "Redes de Computadores", "creditos": 4, "periodo": 4, 
                "ementa": "Estudo dos conceitos fundamentais de redes de computadores, arquitetura de protocolos (modelo OSI/TCP-IP), camadas de aplicação, transporte, rede e enlace."
            },
            {
                "codigo": "MAT1001", "nome": "Cálculo I", "creditos": 6, "periodo": 1, 
                "ementa": "Funções e gráficos; derivadas; aplicações das derivadas; métodos de Newton; integrais indefinidas e equações diferenciais com variáveis separáveis; integral definida; exponencial e logaritmo; funções trigonométricas; métodos de integração numérica e regra de Simpson; regra de L Hôpital."
            },
            {
                "codigo": "INF1010", "nome": "Algoritmos e Estruturas", "creditos": 4, "periodo": 1, 
                "ementa": "Árvores: formas de representação, recursão em árvores, árvores binárias, árvores binárias de busca, filas de prioridades, árvores balanceadas. Heaps e estruturas para partições dinâmicas. Conjuntos: operações, representação por listas e por vetores característicos, hashing. Grafos e algoritmos básicos."
            },
            {
                "codigo": "INF1025", "nome": "Banco de Dados", "creditos": 4, "periodo": 3, 
                "ementa": "Introdução a computadores e a linguagens de programação imperativas. Variáveis, expressões e funções. Controle de fluxo iterações e condicionais. Valores básicos e estruturados. Funções e recursão. Arquivos."
            },
            {
                "codigo": "INF1020", "nome": "Programação Orientada a Objetos", "creditos": 4, "periodo": 2, 
                "ementa": "Conceitos básicos e organização de sistemas de informação; Infra-estrutura de Tecnologia de Informação; Comércio eletrônico, Gerência de conhecimento; Sistemas de apoio à tomada de decisão; Impactos sociais da tecnologia da informação."
            },
            {
                "codigo": "INF1039", "nome": "Projeto de Aplicações", "creditos": 4, "periodo": 3, 
                "ementa": "Uso de ferramenta para aplicações interativas; Elementos de interação, geometria, movimento, colisão, sensores e multimídia; Projetos exploratórios; Desenvolvimento de aplicação interativa; Estratégias de IHC (Interface Humano-Computador); Design conceitual; Requisitos; Fases de ciclo de vida do desenvolvimento; Questões de integração; Avaliação."
            },
        ]
        disciplinas_objs = {}

        for data in DISCIPLINAS:
            disciplina, created = Disciplina.objects.get_or_create(
                codigo=data['codigo'],
                defaults={
                    'nome': data['nome'],
                    'creditos': data['creditos'],
                    'periodo': data['periodo'],
                    'ementa': data.get('ementa', '')
                }
            )
            disciplinas_objs[data['codigo']] = disciplina
            
            if data['codigo'] not in self.logged_codes:
                self.logged_codes.add(data['codigo'])
                if created:
                    self.created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✔ Criado: {disciplina.nome} ({data["codigo"]})'))
                else:
                    self.stdout.write(f'  – Já existe: {disciplina.nome} ({data["codigo"]})')

        REQUISITOS_CONFIG = [
            {'cod': 'INF1045', 'tipo': 'PRE', 'op': 'AND', 'reqs': ['INF1027', 'INF1383', 'INF1636']},
            {'cod': 'MAT1001', 'tipo': 'PRE', 'op': 'AND', 'reqs': ['MAT1000']},
            {'cod': 'INF1010', 'tipo': 'PRE', 'op': 'AND', 'reqs': ['INF1006', 'PORT3']},
            {'cod': 'INF1010', 'tipo': 'PRE', 'op': 'AND', 'reqs': ['INF1007', 'PORT3']},
            {'cod': 'INF1010', 'tipo': 'PRE', 'op': 'AND', 'reqs': ['INF1037', 'PORT3']},
            {'cod': 'INF1010', 'tipo': 'PRE', 'op': 'AND', 'reqs': ['INF1318', 'PORT3']},
            {'cod': 'INF1010', 'tipo': 'PRE', 'op': 'AND', 'reqs': ['INF1620', 'PORT3']},
            {'cod': 'INF1039', 'tipo': 'PRE', 'op': 'OR',  'reqs': ['CTC4002', 'INF1025']},
            {'cod': 'INF1039', 'tipo': 'CO',  'op': 'AND', 'reqs': ['INF1007', 'INF1403']},
            {'cod': 'INF1039', 'tipo': 'CO',  'op': 'AND', 'reqs': ['INF1037', 'INF1403']},
        ]

        for item in REQUISITOS_CONFIG:
            disc_principal = disciplinas_objs.get(item['cod']) or self.get_disc(item['cod'])
            req = Requisito.objects.create(
                disciplina_principal=disc_principal, 
                tipo=item['tipo'], 
                operador=item['op']
            )
            objetos_req = [self.get_disc(r) if isinstance(r, str) else r for r in item['reqs']]
            req.disciplinas.add(*objetos_req)

        self.stdout.write(self.style.SUCCESS(f'\n{self.created_count} disciplina(s) criada(s) com sucesso!'))