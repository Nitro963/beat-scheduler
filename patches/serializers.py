from rest_framework.fields import ChoiceField

from .enum import Enum


class EnumField(ChoiceField):
    def __init__(self, enum: Enum.__class__, **kwargs):
        self.enum = enum
        super().__init__(enum.get_django_choices(), **kwargs)

    def to_representation(self, value):
        return self.enum(value).name
