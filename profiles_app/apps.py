from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProfilesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles_app'
    verbose_name = _('Profiles')

    def ready(self):
        from . import signals # noqa
