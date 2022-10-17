import argparse
import importlib
import importlib.util

import factory.random
from django.conf import settings
from django.core.management.base import BaseCommand

from ...seeder_base import SeederBase


class Command(BaseCommand):
    help = 'Seed django database with random data'

    @staticmethod
    def check_positive(value):
        int_value = int(value)
        if int_value <= 0:
            raise argparse.ArgumentTypeError(f'{value} is an invalid positive int value')
        return int_value

    def add_arguments(self, parser):
        parser.add_argument('-a', '--app', type=str, help='django apps names', nargs='+')
        parser.add_argument('-t', '--table', type=str,
                            help='Database tables names which to include in seeding', nargs='+')
        parser.add_argument('-eA', '--exclude-app', type=str,
                            help='django apps names which to exclude from seeding', nargs='+')
        parser.add_argument('-eT', '--exclude-table', type=str,
                            help='Database tables which to exclude from seeding', nargs='+')
        parser.add_argument('-n', '--number', type=self.check_positive, help='the number of instances', default=10)
        parser.add_argument('-s', '--state', type=int, help='the random state of the seeder. Pass an int for '
                                                            'reproducible output')

    @staticmethod
    def load_seeder(app_name) -> SeederBase:
        seeder_mod = importlib.import_module(f'{app_name}.seeder')
        assert hasattr(seeder_mod, 'Seeder')
        assert issubclass(seeder_mod.Seeder, SeederBase)
        return seeder_mod.Seeder()

    def handle(self, *args, **kwargs):
        if kwargs['state'] is not None:
            factory.random.reseed_random(kwargs['state'])
        exclude_apps = kwargs['exclude_app'] if kwargs['exclude_app'] is not None else []
        exclude_tables = kwargs['exclude_table'] if kwargs['exclude_table'] is not None else []
        include_tables = kwargs['table'] if kwargs['table'] is not None else []
        if kwargs['app'] is not None:
            for app_name in kwargs['app']:
                if app_name not in exclude_apps:
                    if importlib.util.find_spec(f'.seeder', app_name):
                        self.load_seeder(app_name).make_objects(kwargs['number'],
                                                                exclude_tables=exclude_tables,
                                                                include_tables=include_tables)
            return
        for app_name in settings.INSTALLED_APPS:
            if app_name not in exclude_apps:
                try:
                    if importlib.util.find_spec(f'.seeder', app_name):
                        self.load_seeder(app_name).make_objects(kwargs['number'],
                                                                exclude_tables=exclude_tables,
                                                                include_tables=include_tables)
                except ModuleNotFoundError:
                    pass
