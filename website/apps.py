from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name         = 'website'
    verbose_name = '🌐 Website'

    def ready(self):
        import website.signals  # noqa — registers referral & affiliate signal handlers