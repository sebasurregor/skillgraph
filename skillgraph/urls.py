from django.contrib import admin
from django.urls import include, path

from skillgraph.views import portada, salud

urlpatterns = [
    path("", portada, name="raiz"),
    path("salud/", salud, name="salud"),
    path("cuentas/", include("cuentas.urls")),
    path("vacantes/", include("vacantes.urls")),
    path("perfil/", include("perfiles.urls")),
    path("recomendaciones/", include("matching.urls_web")),
    path("postulaciones/", include("postulaciones.urls")),
    path("api/matching/", include("matching.urls")),
    path("admin/", admin.site.urls),
]
