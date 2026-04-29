from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Student


STUDENTS = [
    {"first_name": "Theo",    "last_name": "Lemaire",   "email": "theo@example.com",    "matricula": "2024001"},
    {"first_name": "Jorge",   "last_name": "Silva",     "email": "jorge@example.com",   "matricula": "2024002"},
    {"first_name": "Thiago",  "last_name": "Souza",     "email": "thiago@example.com",  "matricula": "2024003"},
    {"first_name": "Matheus", "last_name": "Costa",     "email": "matheus@example.com", "matricula": "2024004"},
    {"first_name": "Ana",     "last_name": "Oliveira",  "email": "ana@example.com",     "matricula": "2024005"},
    {"first_name": "Lucas",   "last_name": "Ferreira",  "email": "lucas@example.com",   "matricula": "2024006"},
]


class Command(BaseCommand):
    help = 'Popula o banco de dados com estudantes de exemplo'

    def handle(self, *args, **kwargs):
        created_count = 0

        for data in STUDENTS:
            user, user_created = User.objects.get_or_create(
                username=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name':  data['last_name'],
                    'email':      data['email'],
                }
            )

            if user_created:
                user.set_password('password123')
                user.save()

            student, student_created = Student.objects.get_or_create(
                matricula=data['matricula'],
                defaults={'user': user}
            )

            if student_created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✔ Criado: {user.get_full_name()} ({data["matricula"]})'))
            else:
                self.stdout.write(f'  – Já existe: {user.get_full_name()} ({data["matricula"]})')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} estudante(s) criado(s) com sucesso!'))
        self.stdout.write('Senha padrão de todos: password123')
