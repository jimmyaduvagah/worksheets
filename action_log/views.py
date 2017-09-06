from django.shortcuts import render
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsOwnerOrReadOnly
from .serializers import CompanySerializer
from companies.models import Company

# Demo code from DRF
# class SnippetViewSet(viewsets.ModelViewSet):
#     """
#     This endpoint presents code snippets.
#     The `highlight` field presents a hyperlink to the hightlighted HTML
#     representation of the code snippet.
#     The **owner** of the code snippet may update or delete instances
#     of the code snippet.
#     Try it yourself by logging in as one of these four users: **amy**, **max**,
#     **jose** or **aziz**.  The passwords are the same as the usernames.
#     """
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly,
#                           IsOwnerOrReadOnly,)
#
#     @detail_route(renderer_classes=(renderers.StaticHTMLRenderer,))
#     def highlight(self, request, *args, **kwargs):
#         snippet = self.get_object()
#         return Response(snippet.highlighted)
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated,)
