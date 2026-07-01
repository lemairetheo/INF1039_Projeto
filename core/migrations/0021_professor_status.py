# Generated manually to add status and document fields to Professor

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0020_denunciadisciplina"),
    ]

    operations = [
        migrations.AddField(
            model_name="professor",
            name="status",
            field=models.CharField(
                choices=[
                    ("pendente", "Pendente"),
                    ("aprovado", "Aprovado"),
                    ("rejeitado", "Rejeitado"),
                ],
                default="pendente",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="professor",
            name="documento",
            field=models.FileField(
                blank=True, null=True, upload_to="professores/documentos/"
            ),
        ),
        migrations.AddField(
            model_name="professor",
            name="criado_em",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
