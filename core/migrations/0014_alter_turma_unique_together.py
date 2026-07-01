# Generated manually to remove old dia_semana field

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_diasemanaaula_remove_denuncia_data_denuncia_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="turma",
            name="dia_semana",
        ),
    ]
