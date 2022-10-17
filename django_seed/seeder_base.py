from abc import ABC
from typing import Iterable, Dict, Callable, Any


class SeederBase(ABC):
    tables = set()

    def __init__(self):
        self.seeders_table: Dict[str, Callable[[int], Any]] = {name: getattr(self, f'seed_{name}', self.seed_none)
                                                               for name in self.tables}

    def seed_none(self, batch_size):
        pass

    @staticmethod
    def echo_info_and_seed(seed_func: Callable[[int], Any], number, name):
        msg = f'creating {number} {name} instance'
        if number >= 2:
            msg += 's'
        print(msg)
        return seed_func(number)

    def make_objects(self, batch_size, include_tables: Iterable[str] = tuple(),
                     exclude_tables: Iterable[str] = tuple()):

        _include_tables = set(include_tables).intersection(self.tables)

        if not _include_tables and include_tables:
            return

        _exclude_tables = set(exclude_tables).intersection(self.tables)

        tables_to_seed = self.tables - _exclude_tables

        if _include_tables:
            tables_to_seed = _include_tables

        return [self.seeders_table.get(table)(batch_size) for table in tables_to_seed]
