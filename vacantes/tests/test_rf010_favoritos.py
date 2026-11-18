"""HU-RF-010 · Guardar vacantes como favoritos."""
import pytest
from django.urls import reverse

from cuentas.models import Usuario
from vacantes import services
from vacantes.models import Vacante, VacanteFavorita


@pytest.fixture
def ana(demo):
    return Usuario.objects.get(email="ana.rios@correo.com")


@pytest.fixture
def backend(demo):
    return Vacante.objects.get(titulo="Desarrollador Backend Senior")


@pytest.fixture
def sesion(client, ana):
    client.force_login(ana)
    return client


def test_rf010_permite_marcar_y_desmarcar_una_vacante_como_favorita(
    sesion, ana, backend
):
    url = reverse("vacantes:alternar_favorita", args=[backend.pk])
    # Marcar como favorita
    respuesta = sesion.post(url, follow=True)
    assert respuesta.status_code == 200
    assert VacanteFavorita.objects.filter(usuario=ana, vacante=backend).exists()
    assert "Vacante guardada en sus favoritos." in respuesta.content.decode()

    # Desmarcar como favorita
    respuesta = sesion.post(url, follow=True)
    assert not VacanteFavorita.objects.filter(usuario=ana, vacante=backend).exists()
    assert "Vacante retirada de sus favoritos." in respuesta.content.decode()


def test_rf010_ofrece_seccion_dedicada_para_visualizar_vacantes_guardadas(
    sesion, ana, backend
):
    services.alternar_favorita(ana, backend.pk)
    html = sesion.get(reverse("vacantes:favoritas")).content.decode()
    assert "Vacantes que le gustaron" in html
    assert "Desarrollador Backend Senior" in html
    assert f'data-vacante="{backend.pk}"' in html


def test_rf010_permite_eliminar_vacantes_de_la_lista_de_favoritos(
    sesion, ana, backend
):
    services.alternar_favorita(ana, backend.pk)
    url = reverse("vacantes:eliminar_favorita", args=[backend.pk])
    respuesta = sesion.post(url, follow=True)
    assert respuesta.status_code == 200
    assert not VacanteFavorita.objects.filter(usuario=ana, vacante=backend).exists()
    assert "Todavía no ha guardado vacantes" in respuesta.content.decode()
