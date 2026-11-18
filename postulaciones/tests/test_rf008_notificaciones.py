"""HU-RF-008 · Notificar cambio de estado en postulaciones."""
import pytest
from django.core import mail
from django.urls import reverse

from cuentas.models import Usuario
from postulaciones import services
from postulaciones.models import NotificacionPostulacion, Postulacion
from vacantes.models import Vacante


@pytest.fixture
def ana(demo):
    return Usuario.objects.get(email="ana.rios@correo.com")


@pytest.fixture
def backend(demo):
    return Vacante.objects.get(titulo="Desarrollador Backend Senior")


@pytest.fixture
def postulacion_ana(ana, backend):
    postulacion, _ = services.postular(ana, backend.pk)
    return postulacion


def test_rf008_envia_notificaciones_cuando_es_vista_aceptada_o_rechazada(
    postulacion_ana,
):
    for estado_alias, estado_real in (
        ("vista", Postulacion.Estado.EN_REVISION),
        ("aceptada", Postulacion.Estado.PRESELECCIONADA),
        ("rechazada", Postulacion.Estado.DESCARTADA),
    ):
        services.cambiar_estado(postulacion_ana, estado_alias)
        notif = NotificacionPostulacion.objects.filter(
            postulacion=postulacion_ana, estado=estado_real
        ).first()
        assert notif is not None
        assert notif.enviada_plataforma is True
        assert notif.enviada_correo is True

    assert NotificacionPostulacion.objects.count() == 3
    assert len(mail.outbox) == 3


def test_rf008_permite_configurar_el_canal_de_notificacion(
    client, ana, postulacion_ana
):
    client.force_login(ana)
    # Desactiva correo y deja solo plataforma
    client.post(
        reverse("postulaciones:configurar_notificaciones"),
        {"notificar_plataforma": "on"},
    )
    mail.outbox.clear()
    services.cambiar_estado(postulacion_ana, Postulacion.Estado.PRESELECCIONADA)

    notif = NotificacionPostulacion.objects.get()
    assert notif.enviada_plataforma is True
    assert notif.enviada_correo is False
    assert len(mail.outbox) == 0


def test_rf008_el_historico_de_notificaciones_es_accesible_para_el_usuario(
    client, ana, postulacion_ana
):
    services.cambiar_estado(postulacion_ana, Postulacion.Estado.EN_REVISION)
    services.cambiar_estado(postulacion_ana, Postulacion.Estado.PRESELECCIONADA)

    client.force_login(ana)
    html = client.get(reverse("postulaciones:mias")).content.decode()
    assert "Histórico de notificaciones (2)" in html
    assert "Desarrollador Backend Senior" in html
    assert html.count("data-notificacion=") == 2
