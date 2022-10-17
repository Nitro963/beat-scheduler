# This will make sure the app is always imported and the correct environment variables is always loaded when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)
