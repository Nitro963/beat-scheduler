import pytest
from django.contrib.auth import authenticate

from ..models import UserProfile


@pytest.mark.django_db
def test_new_user(user_factory):
    user = user_factory.create()
    assert user.is_active
    assert not user.is_staff
    assert authenticate(request=None, username=user.email, password='123456789') is not None


@pytest.mark.django_db
def test_new_users(user_factory):
    batch = user_factory.create_batch(100)
    assert UserProfile.objects.count() == 100
    for user in batch:
        assert authenticate(request=None, username=user.email, password='123456789') is not None
