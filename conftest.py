import os

import factory.random
import pytest
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save, pre_save
from factory.django import mute_signals
from pytest_factoryboy import register
from rest_framework.test import APIClient

from profiles_app.factories import UserFactory

factory.random.reseed_random(44)

register(UserFactory)


@pytest.mark.django_db
@pytest.fixture
@mute_signals(post_save, pre_save)
def auth_user(user_factory):
    return user_factory.create(email='user@test.com', password=make_password('password'))


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(scope='session')
def celery_app(celery_config, celery_parameters, celery_enable_logging, use_celery_app_trap):
    from beat_scheduler.celery import app
    return app


@pytest.fixture(scope='session')
def celery_worker(celery_app, celery_includes, celery_worker_pool, celery_worker_parameters):
    from celery.contrib.testing import worker
    from celery.contrib.pytest import NO_WORKER
    if not NO_WORKER:
        for module in celery_includes:
            celery_app.loader.import_task_module(module)
        with worker.start_worker(celery_app,
                                 pool=celery_worker_pool,
                                 **celery_worker_parameters) as w:
            yield w


@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {'queues': os.environ.get('WORKERS_QUEUES', 'celery_default,celery_hello'),
            'shutdown_timeout': 30,
            'perform_ping_check': False}
