from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from cuentas.models import Usuario

class Command(BaseCommand):
    help = 'Elimina cuentas que solicitaron borrado hace más de 30 días (HU-RNF-007)'

    def handle(self, *args, **kwargs):
        limite = timezone.now() - timedelta(days=30)
        usuarios_a_borrar = Usuario.objects.filter(solicitud_eliminacion_en__lte=limite)
        
        cantidad = usuarios_a_borrar.count()
        if cantidad > 0:
            usuarios_a_borrar.delete()
            self.stdout.write(self.style.SUCCESS(f'{cantidad} usuarios eliminados permanentemente.'))
        else:
            self.stdout.write(self.style.SUCCESS('No hay cuentas pendientes por eliminar.'))