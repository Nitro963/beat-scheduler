import functools
from django_seed.seeder_base import SeederBase
from .factories import UserFactory


class Seeder(SeederBase):
    tables = {'user_profile'}

    def seed_user_profile(self, batch_size):
        self.echo_info_and_seed(UserFactory.create_batch, batch_size - 1, 'user')
        self.echo_info_and_seed(functools.partial(UserFactory.create_batch, email='admin@example.com',
                                                  is_staff=True, is_superuser=True), 1, 'admin')
