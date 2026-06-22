from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Executa migrate e depois o scraper"

    def handle(self, *args, **kwargs):
        call_command("migrate")
        call_command("micro_puc")