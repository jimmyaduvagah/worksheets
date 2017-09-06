from django.shortcuts import render
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import CountrySerializer, StateSerializer
from .models import Country, State



class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAuthenticated,)


class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        queryset = self.queryset.filter()

        country_filter = request.GET.get('country_id', False)
        if country_filter != False:
            queryset = queryset.filter(country_id=country_filter)


        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)
