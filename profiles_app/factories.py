from django.contrib.auth.hashers import make_password
from factory import post_generation
from factory.django import DjangoModelFactory
from factory.faker import Faker

from .enums import Gender
from .models import UserProfile


class UserFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile
        django_get_or_create = ('email',)

    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    birthday = Faker('date_of_birth', minimum_age=16, maximum_age=60)
    password = make_password('123456789')
    is_active = True
    is_staff = False
    is_superuser = False
    date_joined = Faker('date')
    gender = Faker('random_element', elements=Gender.get_values())

    @post_generation
    def groups(self, create, extracted, **kwargs): # noqa
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            self.groups.set(extracted)
            return

        # self.groups.set([2])  # default group
