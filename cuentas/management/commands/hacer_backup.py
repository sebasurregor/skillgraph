import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Realiza un respaldo de la base de datos (SQLite o PostgreSQL)'

    def handle(self, *args, **kwargs):
        # 1. Crear la carpeta 'backups' si no existe
        backup_dir = Path(settings.BASE_DIR) / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_settings = settings.DATABASES['default']
        engine = db_settings['ENGINE']

        self.stdout.write(f"Iniciando respaldo de la base de datos ({engine})...")

        # 2. Lógica para SQLite (Desarrollo Local)
        if 'sqlite3' in engine:
            db_path = db_settings['NAME']
            backup_path = backup_dir / f'db_backup_{timestamp}.sqlite3'
            
            # Copiamos el archivo físico
            shutil.copy2(db_path, backup_path)
            
            self.stdout.write(
                self.style.SUCCESS(f'Respaldo SQLite creado exitosamente en: {backup_path}')
            )

        # 3. Lógica para PostgreSQL (Producción / Supabase)
        elif 'postgresql' in engine or 'postgres' in engine:
            backup_path = backup_dir / f'db_backup_{timestamp}.sql'
            
            # Construimos el comando pg_dump
            cmd = [
                'pg_dump',
                '-h', db_settings.get('HOST', 'localhost'),
                '-p', str(db_settings.get('PORT', '5432')),
                '-U', db_settings.get('USER', 'postgres'),
                '-F', 'c',  # Formato custom (comprimido)
                '-b',       # Incluir objetos grandes (hojas de vida, etc.)
                '-f', str(backup_path),
                db_settings.get('NAME', 'postgres')
            ]
            
            # Usamos una variable de entorno temporal para la contraseña (seguridad)
            env = os.environ.copy()
            env['PGPASSWORD'] = db_settings.get('PASSWORD', '')
            
            try:
                # Ejecutamos pg_dump
                subprocess.run(cmd, env=env, check=True)
                self.stdout.write(
                    self.style.SUCCESS(f'Respaldo PostgreSQL creado exitosamente en: {backup_path}')
                )
            except subprocess.CalledProcessError as e:
                self.stderr.write(self.style.ERROR(f'Error al crear el respaldo: {e}'))
            except FileNotFoundError:
                self.stderr.write(
                    self.style.ERROR('pg_dump no está instalado. Instala las herramientas de PostgreSQL para usar esta función.')
                )
        else:
            self.stderr.write(self.style.ERROR('Motor de base de datos no soportado para respaldos.'))