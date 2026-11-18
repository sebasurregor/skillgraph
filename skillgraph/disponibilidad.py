"""Monitoreo de disponibilidad y tiempos de respuesta (HU-RNF-003)."""
import math
import threading
import time
from collections import deque

from django.db import connections

HORAS_MES = 720.0
SLA_DISPONIBILIDAD_MENSUAL = 99.0
MAX_HORAS_INACTIVIDAD_MES = 7.2
UMBRAL_RESPUESTA_S = 3.0
PERCENTIL_CUMPLIMIENTO = 95.0


class MonitorDisponibilidad:
    """Registra tiempos de respuesta y verifica el cumplimiento de HU-RNF-003."""

    def __init__(self, max_muestras=2000):
        self._candado = threading.Lock()
        self.tiempos = deque(maxlen=max_muestras)
        self.total = 0
        self.fallidas = 0

    def registrar(self, duracion_s, status_code):
        with self._candado:
            self.total += 1
            self.tiempos.append(float(duracion_s))
            if status_code >= 500:
                self.fallidas += 1

    def reiniciar(self):
        with self._candado:
            self.tiempos.clear()
            self.total = 0
            self.fallidas = 0

    @staticmethod
    def disponibilidad_mensual(horas_inactividad):
        disponibilidad = ((HORAS_MES - horas_inactividad) / HORAS_MES) * 100.0
        return {
            "disponibilidad_pct": round(disponibilidad, 2),
            "horas_inactividad": round(horas_inactividad, 2),
            "max_horas_inactividad": MAX_HORAS_INACTIVIDAD_MES,
            "cumple_sla": (
                disponibilidad >= SLA_DISPONIBILIDAD_MENSUAL
                and horas_inactividad <= MAX_HORAS_INACTIVIDAD_MES
            ),
        }

    def resumen(self):
        with self._candado:
            muestras = list(self.tiempos)
            total = self.total
            fallidas = self.fallidas
        if not muestras:
            return {
                "total": 0,
                "promedio_s": 0.0,
                "p95_s": 0.0,
                "pct_bajo_umbral": 100.0,
                "disponibilidad_pct": 100.0,
                "cumple": True,
            }
        promedio = sum(muestras) / len(muestras)
        ordenadas = sorted(muestras)
        idx_p95 = max(
            0, math.ceil((PERCENTIL_CUMPLIMIENTO / 100.0) * len(ordenadas)) - 1
        )
        p95 = ordenadas[idx_p95]
        bajo_umbral = sum(1 for t in muestras if t <= UMBRAL_RESPUESTA_S)
        pct_bajo_umbral = (bajo_umbral / len(muestras)) * 100.0
        disponibilidad_pct = ((total - fallidas) / total) * 100.0
        cumple = (
            promedio < UMBRAL_RESPUESTA_S
            and pct_bajo_umbral >= PERCENTIL_CUMPLIMIENTO
            and disponibilidad_pct >= SLA_DISPONIBILIDAD_MENSUAL
        )
        return {
            "total": total,
            "promedio_s": round(promedio, 4),
            "p95_s": round(p95, 4),
            "pct_bajo_umbral": round(pct_bajo_umbral, 2),
            "disponibilidad_pct": round(disponibilidad_pct, 2),
            "cumple": cumple,
        }


monitor = MonitorDisponibilidad()


class DisponibilidadMiddleware:
    """Mide la latencia de cada solicitud para HU-RNF-003."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        inicio = time.perf_counter()
        response = self.get_response(request)
        duracion = time.perf_counter() - inicio
        monitor.registrar(duracion, response.status_code)
        response["X-Response-Time-Seconds"] = f"{duracion:.4f}"
        return response


def estado_salud():
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        bd_ok = True
    except Exception:
        bd_ok = False
    return {
        "disponible": bd_ok,
        "sla": monitor.resumen(),
    }
