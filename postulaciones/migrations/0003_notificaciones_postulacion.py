import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("postulaciones", "0002_perfil_al_postular"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PreferenciaNotificacion",
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
                ("notificar_plataforma", models.BooleanField(default=True)),
                ("notificar_correo", models.BooleanField(default=True)),
                ("actualizada_en", models.DateTimeField(auto_now=True)),
                (
                    "usuario",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="preferencias_notificacion",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "preferencia de notificación",
                "verbose_name_plural": "preferencias de notificación",
            },
        ),
        migrations.CreateModel(
            name="NotificacionPostulacion",
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
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("enviada", "Enviada"),
                            ("en_revision", "En revisión"),
                            ("preseleccionada", "Preseleccionada"),
                            ("descartada", "Descartada"),
                        ],
                        max_length=16,
                    ),
                ),
                ("mensaje", models.CharField(max_length=280)),
                ("enviada_plataforma", models.BooleanField(default=True)),
                ("enviada_correo", models.BooleanField(default=False)),
                ("leida", models.BooleanField(default=False)),
                ("creada_en", models.DateTimeField(auto_now_add=True)),
                (
                    "postulacion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notificaciones",
                        to="postulaciones.postulacion",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notificaciones_postulacion",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "notificación de postulación",
                "verbose_name_plural": "notificaciones de postulaciones",
                "ordering": ["-creada_en"],
            },
        ),
    ]
