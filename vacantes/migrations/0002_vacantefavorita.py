import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vacantes", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="VacanteFavorita",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("creada_en", models.DateTimeField(auto_now_add=True)),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favoritas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vacante",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favoritos",
                        to="vacantes.vacante",
                    ),
                ),
            ],
            options={
                "verbose_name": "vacante favorita",
                "verbose_name_plural": "vacantes favoritas",
                "ordering": ["-creada_en"],
            },
        ),
        migrations.AddConstraint(
            model_name="vacantefavorita",
            constraint=models.UniqueConstraint(
                fields=("usuario", "vacante"),
                name="una_favorita_por_usuario_y_vacante",
            ),
        ),
    ]
