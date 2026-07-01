# Generated manually to add data_denuncia field with default

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0018_curriculo_student_curriculo_curriculoitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="denuncia",
            name="data_denuncia",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
