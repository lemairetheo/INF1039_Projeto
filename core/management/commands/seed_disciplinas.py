from django.core.management.base import BaseCommand
from core.models import Disciplina, Professor


DISCIPLINAS = [
    {"codigo": "INF1039", "nome": "Projeto de Aplicações",      "creditos": 4, "periodo": 3, "prof": "Carlos Mendes"},
    {"codigo": "INF1020", "nome": "Programação Orientada a Objetos", "creditos": 4, "periodo": 2, "prof": "Ana Beatriz Lima"},
    {"codigo": "INF1025", "nome": "Banco de Dados",             "creditos": 4, "periodo": 3, "prof": "Roberto Farias"},
    {"codigo": "INF1010", "nome": "Algoritmos e Estruturas",    "creditos": 4, "periodo": 1, "prof": "Carlos Mendes"},
    {"codigo": "MAT1001", "nome": "Cálculo I",                  "creditos": 6, "periodo": 1, "prof": "Paula Gomes"},
    {"codigo": "INF1045", "nome": "Redes de Computadores",      "creditos": 4, "periodo": 4, "prof": "Marcos Alves"},
    {"codigo": "INF1030", "nome": "Engenharia de Software",     "creditos": 4, "periodo": 3, "prof": "Roberto Farias"},
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com disciplinas de exemplo'

    def handle(self, *args, **kwargs):
        created_count = 0

        for data in DISCIPLINAS:
            professor = Professor.objects.filter(nome=data['prof']).first()

            if not professor:
                self.stdout.write(self.style.WARNING(f'  ⚠ Professor não encontrado: {data["prof"]} — rode seed_professors primeiro'))
                continue

            disciplina, created = Disciplina.objects.get_or_create(
                codigo=data['codigo'],
                defaults={
                    'nome':      data['nome'],
                    'creditos':  data['creditos'],
                    'periodo':   data['periodo'],
                    'professor': professor,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✔ Criado: {disciplina.codigo} — {disciplina.nome}'))
            else:
                self.stdout.write(f'  – Já existe: {disciplina.codigo}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} disciplina(s) criada(s) com sucesso!'))
