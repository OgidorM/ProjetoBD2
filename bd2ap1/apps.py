from django.apps import AppConfig


class Bd2Ap1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bd2ap1'
    def ready(self):
        import bd2ap1.signals