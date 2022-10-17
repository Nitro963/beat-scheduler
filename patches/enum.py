from enum import Enum


class Enum(Enum):
    @classmethod
    def get_django_choices(cls):
        return [
            (e.value, e.name) for e in cls
        ]

    @classmethod
    def get_values(cls):
        return [e.value for e in cls]

    @classmethod
    def get_names(cls):
        return [e.name for e in cls]
