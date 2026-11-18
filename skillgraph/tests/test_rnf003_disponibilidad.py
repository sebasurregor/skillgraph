"""HU-RNF-003 · Generar disponibilidad del sistema."""
import pytest
from django.urls import reverse

from skillgraph.disponibilidad import MonitorDisponibilidad, monitor


def test_rnf003_disponibilidad_promedio_99_por_ciento_mensual():
    # Máximo 7.2 horas de inactividad al mes sobre 720 horas = 99.0%
    en_limite = MonitorDisponibilidad.disponibilidad_mensual(7.2)
    assert en_limite["disponibilidad_pct"] == 99.0
    assert en_limite["cumple_sla"] is True

    # Más de 7.2 horas incumple el SLA
    fuera_limite = MonitorDisponibilidad.disponibilidad_mensual(7.5)
    assert fuera_limite["disponibilidad_pct"] < 99.0
    assert fuera_limite["cumple_sla"] is False


@pytest.mark.django_db
def test_rnf003_100_usuarios_concurrentes_promedio_menor_a_3s_y_95_pct_en_umbral(
    client,
):
    monitor.reiniciar()
    url = reverse("salud")

    respuestas = [client.get(url) for _ in range(100)]
    assert all(r.status_code == 200 for r in respuestas)
    assert all("X-Response-Time-Seconds" in r for r in respuestas)

    resumen = monitor.resumen()
    assert resumen["total"] == 100
    assert resumen["promedio_s"] < 3.0
    assert resumen["pct_bajo_umbral"] >= 95.0
    assert resumen["disponibilidad_pct"] >= 99.0
    assert resumen["cumple"] is True
