from django.apps import AppConfig


class AppsGestaoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps_gestao'

    def ready(self):
        import apps_gestao.signals # Isto ativa os avisos automáticos