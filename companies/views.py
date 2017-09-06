from django.shortcuts import render
from rest_framework import permissions, filters
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from time_stream_api.rest_extensions import CreatedModifiedByCreateModelMixin
from .permissions import IsOwnerOrReadOnly
from .serializers import CompanySerializer
from .models import Company



class CompanyViewSet(CreatedModifiedByCreateModelMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    search_fields = ('name',)

    def list(self, request, *args, **kwargs):
        self.admin_check(request);
        return super(CompanyViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.admin_check(request);
        return super(CompanyViewSet, self).retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.admin_check(request);
        return super(CompanyViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.admin_check(request);
        return super(CompanyViewSet, self).destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.admin_check(request);
        return super(CompanyViewSet, self).update(request, *args, **kwargs)

    def admin_check(self, request):
        if request.user.is_superuser or request.user.is_staff or request.user.userprofile.is_admin:
            pass
        else:
            raise Exception('Not Allowed')

