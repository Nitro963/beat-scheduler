from django_filters import filters, filterset
from rest_framework.filters import BaseFilterBackend

from . import models


class UserProfileFilter(filterset.FilterSet):
    birthday = filters.DateFromToRangeFilter()

    class Meta:
        model = models.UserProfile
        fields = ['gender', 'birthday']


class FilterIsOwnerBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if user.is_staff:
            return queryset
        return queryset.filter(pk=user.pk)
