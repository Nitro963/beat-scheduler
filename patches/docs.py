from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularRedocView
from rest_framework import viewsets


class DocsViewSet(viewsets.ViewSetMixin, SpectacularRedocView):
    @extend_schema(exclude=True)
    def list(self, request):
        return super(DocsViewSet, self).get(request)
