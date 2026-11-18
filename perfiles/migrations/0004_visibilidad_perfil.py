from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("perfiles", "0003_preferencias_laborales"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfilcandidato",
            name="visibilidad",
            field=models.CharField(
                choices=[("publico", "Público"), ("privado", "Privado")],
                default="publico",
                help_text="Define si los datos personales y la hoja de vida son visibles.",
                max_length=10,
            ),
        ),
    ]
