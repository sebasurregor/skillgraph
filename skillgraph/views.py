from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect

from perfiles import services as perfiles
from skillgraph.disponibilidad import estado_salud


@login_required
def portada(request):
    """Lleva a cada usuario a su punto de partida.

    Flujo resume-first: al candidato sin perfil confirmado lo primero que se le
    ofrece es subir su hoja de vida.
    """
    usuario = request.user
    if usuario.es_reclutador:
        return redirect("vacantes:lista")
    if not perfiles.tiene_perfil_confirmado(usuario):
        return redirect("perfiles:cargar_cv")
    return redirect("recomendaciones:lista")


def salud(request):
    """Endpoint de disponibilidad del sistema (HU-RNF-003)."""
    datos = estado_salud()
    return JsonResponse(datos, status=200 if datos["disponible"] else 503)
