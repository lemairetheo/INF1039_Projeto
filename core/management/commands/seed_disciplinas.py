from django.core.management.base import BaseCommand
from core.models import Disciplina


DISCIPLINAS = [
    {"codigo": "INF1039", "nome": "Projeto de Aplicações",           "creditos": 4, "periodo": 3},
    {"codigo": "INF1020", "nome": "Programação Orientada a Objetos", "creditos": 4, "periodo": 2},
    {"codigo": "INF1025", "nome": "Banco de Dados",                  "creditos": 4, "periodo": 3},
    {"codigo": "INF1010", "nome": "Algoritmos e Estruturas",         "creditos": 4, "periodo": 1},
    {"codigo": "MAT1001", "nome": "Cálculo I",                       "creditos": 6, "periodo": 1},
    {"codigo": "INF1045", "nome": "Redes de Computadores",           "creditos": 4, "periodo": 4},
    {"codigo": "INF1030", "nome": "Engenharia de Software",          "creditos": 4, "periodo": 3},
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com disciplinas de exemplo'

    def handle(self, *args, **kwargs):
        created_count = 0

        for data in DISCIPLINAS:
            disciplina, created = Disciplina.objects.get_or_create(
                codigo=data['codigo'],
                defaults={
                    'nome':     data['nome'],
                    'creditos': data['creditos'],
                    'periodo':  data['periodo'],
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✔ Criado: {disciplina.codigo} — {disciplina.nome}'))
            else:
                self.stdout.write(f'  – Já existe: {disciplina.codigo}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} disciplina(s) criada(s) com sucesso!'))
