from django.core.management.base import BaseCommand
from core.models import Professor


PROFESSORS = [
    {"nome": "Carlos Mendes",    "departamento": "Ciência da Computação"},
    {"nome": "Ana Beatriz Lima", "departamento": "Sistemas de Informação"},
    {"nome": "Roberto Farias",   "departamento": "Engenharia de Software"},
    {"nome": "Paula Gomes",      "departamento": "Matemática Aplicada"},
    {"nome": "Marcos Alves",     "departamento": "Redes e Segurança"},
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com professores de exemplo'

    def handle(self, *args, **kwargs):
        created_count = 0

        for data in PROFESSORS:
            professor, created = Professor.objects.get_or_create(
                nome=data['nome'],
                defaults={'departamento': data['departamento']}
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✔ Criado: {professor.nome} — {professor.departamento}'))
            else:
                self.stdout.write(f'  – Já existe: {professor.nome}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} professor(es) criado(s) com sucesso!'))
