from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from cuentas import services
from cuentas.forms import ClaveForm, CorreoForm, RegistroForm

import json
from django.http import HttpResponse
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from perfiles.models import PerfilCandidato

SESION_CORREO = "correo_ingreso"


def ingresar(request):
    """Paso 1: pide el correo y decide entre inicio de sesión y registro."""
    if request.user.is_authenticated:
        return redirect("cuentas:inicio")
    form = CorreoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        correo = form.cleaned_data["correo"]
        request.session[SESION_CORREO] = correo
        if services.existe_cuenta(correo):
            return redirect("cuentas:ingresar_clave")
        return redirect("cuentas:registro")
    return render(request, "cuentas/ingresar.html", {"form": form})


def ingresar_clave(request):
    """Paso 2: pide la contraseña de la cuenta existente."""
    if request.user.is_authenticated:
        return redirect("cuentas:inicio")
    correo = request.session.get(SESION_CORREO)
    if not correo:
        return redirect("cuentas:ingresar")
    form = ClaveForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if services.iniciar_sesion(request, correo, form.cleaned_data["clave"]):
            return redirect("raiz")
        form.add_error("clave", "Las credenciales no coinciden. Verifique su contraseña.")
        form.marcar_invalidos()
    return render(request, "cuentas/ingresar_clave.html", {"form": form, "correo": correo})


def registro(request):
    if request.user.is_authenticated:
        return redirect("cuentas:inicio")
    correo = request.session.get(SESION_CORREO, "")
    form = RegistroForm(request.POST or None, initial={"correo": correo})
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        usuario = services.registrar_usuario(
            correo=d["correo"], clave=d["clave"], nombres=d["nombres"],
            apellidos=d["apellidos"], telefono=d["telefono"], ciudad=d["ciudad"],
            rol=d["rol"], empresa=d["empresa"], acepta_datos=d["acepta_datos"],
            acepta_compartir=d["acepta_compartir_empresas"],
        )
        services.registrar_trazabilidad(usuario, "CREACION_CUENTA", request=request)
        request.session[SESION_CORREO] = usuario.email
        messages.success(request, "Su cuenta fue creada correctamente. Ingrese la contraseña "
                                  "que acaba de definir para continuar.")
        return redirect("cuentas:ingresar_clave")
    return render(request, "cuentas/registro.html", {"form": form, "correo": correo})


@require_POST
def salir(request):
    services.cerrar_sesion(request)
    messages.info(request, "Sesión cerrada.")
    return redirect("cuentas:ingresar")


@login_required
def inicio(request):
    return render(request, "cuentas/inicio.html")

@login_required
def solicitar_eliminacion(request):
    """Marca la cuenta para ser eliminada en 30 días."""
    if request.method == "POST":
        usuario = request.user
        usuario.solicitud_eliminacion_en = timezone.now()
        usuario.save()
        services.registrar_trazabilidad(usuario, "SOLICITUD_ELIMINACION", request=request)
        messages.warning(
            request, 
            "Su solicitud de eliminación ha sido registrada. Sus datos serán "
            "borrados permanentemente en un máximo de 30 días."
        )
        return redirect("raiz")
    return render(request, "cuentas/confirmar_eliminacion.html")

@login_required
def exportar_datos(request):
    """Descarga un JSON con toda la información del usuario."""
    usuario = request.user
    perfil = PerfilCandidato.objects.filter(usuario=usuario).first()
    
    datos = {
        "cuenta": {
            "email": usuario.email,
            "nombres": usuario.first_name,
            "apellidos": usuario.last_name,
            "telefono": usuario.telefono,
            "ciudad": usuario.ciudad,
            "empresa": usuario.empresa,
            "fecha_registro": usuario.date_joined,
            "consentimiento_compartir": usuario.consentimiento_compartir_empresas,
            "solicitud_eliminacion": usuario.solicitud_eliminacion_en,
        },
        "perfil_candidato": {},
        "habilidades": []
    }
    
    if perfil:
        datos["perfil_candidato"] = {
            "nombre_completo": perfil.nombre_completo,
            "correo_contacto": perfil.correo,
            "telefono": perfil.telefono,
            "experiencia": perfil.experiencia,
            "educacion": perfil.educacion,
        }
        datos["habilidades"] = [
            {"habilidad": h.habilidad.nombre, "nivel": h.nivel} 
            for h in perfil.habilidades.all()
        ]
        
    # Generar la descarga del archivo JSON
    response = HttpResponse(
        json.dumps(datos, cls=DjangoJSONEncoder, indent=4, ensure_ascii=False),
        content_type="application/json"
    )
    response['Content-Disposition'] = 'attachment; filename="mis_datos_skillgraph.json"'
    return response