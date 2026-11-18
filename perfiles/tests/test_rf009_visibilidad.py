"""HU-RF-009 · Configurar visibilidad de perfil."""
import pytest
from django.urls import reverse

from cuentas.models import Usuario
from perfiles import services
from perfiles.models import PerfilCandidato


@pytest.fixture
def ana(demo):
    return Usuario.objects.get(email="ana.rios@correo.com")


@pytest.fixture
def reclutador(demo):
    return Usuario.objects.filter(rol=Usuario.Rol.RECLUTADOR).first()


def test_rf009_permite_configurar_el_perfil_como_publico_o_privado(client, ana):
    client.force_login(ana)
    respuesta = client.post(
        reverse("perfiles:visibilidad"), {"visibilidad": "privado"}, follow=True
    )
    ana.perfil.refresh_from_db()
    assert ana.perfil.visibilidad == PerfilCandidato.Visibilidad.PRIVADO
    assert "Su perfil ahora es privado." in respuesta.content.decode()


def test_rf009_oculta_o_muestra_datos_personales_segun_configuracion(
    client, ana, reclutador
):
    url = reverse("perfiles:ver_perfil", args=[ana.perfil.pk])
    client.force_login(reclutador)

    # Por defecto es público: muestra correo y teléfono
    html_publico = client.get(url).content.decode()
    assert 'data-datos-personales="visibles"' in html_publico
    assert ana.email in html_publico

    # Al cambiar a privado: oculta correo, teléfono y hoja de vida para terceros
    services.cambiar_visibilidad(ana.perfil, PerfilCandidato.Visibilidad.PRIVADO)
    html_privado = client.get(url).content.decode()
    assert 'data-datos-personales="ocultos"' in html_privado
    assert ana.email not in html_privado
    assert ana.telefono not in html_privado


def test_rf009_permite_cambiar_la_visibilidad_en_cualquier_momento(client, ana):
    client.force_login(ana)
    for estado in ("privado", "publico", "privado", "publico"):
        client.post(reverse("perfiles:visibilidad"), {"visibilidad": estado})
        ana.perfil.refresh_from_db()
        assert ana.perfil.visibilidad == estado
