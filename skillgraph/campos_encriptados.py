# skillgraph/campos_encriptados.py
from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models

class EncryptedCharField(models.CharField):
    """Campo de texto corto que se encripta antes de guardarse en la BD."""
    def __init__(self, *args, **kwargs):
        # Aumentamos el max_length temporalmente para que quepa el texto encriptado
        if 'max_length' in kwargs:
            kwargs['max_length'] *= 2
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        if value is None or value == "":
            return value
        f = Fernet(settings.ENCRYPTION_KEY.encode())
        return f.encrypt(str(value).encode()).decode()

    def from_db_value(self, value, expression, connection):
        if value is None or value == "":
            return value
        f = Fernet(settings.ENCRYPTION_KEY.encode())
        try:
            return f.decrypt(value.encode()).decode()
        except Exception:
            return value # Si falla (ej. datos viejos), devuelve el original

class EncryptedTextField(models.TextField):
    """Campo de texto largo que se encripta antes de guardarse en la BD."""
    def get_prep_value(self, value):
        if value is None or value == "":
            return value
        f = Fernet(settings.ENCRYPTION_KEY.encode())
        return f.encrypt(str(value).encode()).decode()

    def from_db_value(self, value, expression, connection):
        if value is None or value == "":
            return value
        f = Fernet(settings.ENCRYPTION_KEY.encode())
        try:
            return f.decrypt(value.encode()).decode()
        except Exception:
            return value