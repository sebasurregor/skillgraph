from django.conf import settings
from django.db import models

from perfiles.models import PerfilCandidato
from vacantes.models import Vacante


class Postulacion(models.Model):
    """Un candidato se postula a una vacante. Solo puede hacerlo una vez."""

    class Estado(models.TextChoices):
        ENVIADA = "enviada", "Enviada"
        EN_REVISION = "en_revision", "En revisión"
        PRESELECCIONADA = "preseleccionada", "Preseleccionada"
        DESCARTADA = "descartada", "Descartada"

    candidato = models.ForeignKey(PerfilCandidato, on_delete=models.CASCADE,
                                  related_name="postulaciones")
    vacante = models.ForeignKey(Vacante, on_delete=models.CASCADE, related_name="postulaciones")
    estado = models.CharField(max_length=16, choices=Estado.choices, default=Estado.ENVIADA)
    ajuste_al_postular = models.PositiveSmallIntegerField(
        help_text="Porcentaje de match en el momento de postularse.")
    perfil_al_postular = models.JSONField(
        default=dict, blank=True,
        help_text="Fotografía del perfil en el momento de postularse: datos de contacto, "
                  "experiencia, educación, habilidades con su nivel y hoja de vida.")
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creada_en"]
        verbose_name = "postulación"
        verbose_name_plural = "postulaciones"
        constraints = [models.UniqueConstraint(fields=["candidato", "vacante"],
                                               name="una_postulacion_por_vacante")]

    def __str__(self):
        return f"{self.candidato.usuario} → {self.vacante}"


class PreferenciaNotificacion(models.Model):
    """Configuración de los canales de notificación del candidato (HU-RF-008)."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="preferencias_notificacion",
    )
    notificar_plataforma = models.BooleanField(default=True)
    notificar_correo = models.BooleanField(default=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "preferencia de notificación"
        verbose_name_plural = "preferencias de notificación"

    def __str__(self):
        return f"Canales de notificación de {self.usuario}"


class NotificacionPostulacion(models.Model):
    """Histórico de notificaciones enviadas al candidato (HU-RF-008)."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones_postulacion",
    )
    postulacion = models.ForeignKey(
        Postulacion,
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    estado = models.CharField(max_length=16, choices=Postulacion.Estado.choices)
    mensaje = models.CharField(max_length=280)
    enviada_plataforma = models.BooleanField(default=True)
    enviada_correo = models.BooleanField(default=False)
    leida = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creada_en"]
        verbose_name = "notificación de postulación"
        verbose_name_plural = "notificaciones de postulaciones"

    def __str__(self):
        return f"{self.usuario} · {self.postulacion.vacante} ({self.estado})"
