import os

from celery import Celery
from sentry_sdk import init as init_sentry
from sentry_sdk.integrations.celery import CeleryIntegration
from celery import signals

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beat_scheduler.settings')

app = Celery('beat_scheduler')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@signals.celeryd_init.connect
def on_celery_init(sender, instance, conf, options, **kwargs):  # noqa
    sentry_dsn = conf.get('SENTRY_DSN', None)
    if sentry_dsn:
        init_sentry(
            dsn=sentry_dsn,
            integrations=[
                CeleryIntegration(),
            ],

            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production,
            traces_sample_rate=conf.get('sentry_traces_sample_rate', 1.0),
        )
