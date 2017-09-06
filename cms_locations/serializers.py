from .models import Country, State
from rest_framework import serializers
from worksheet.rest_extensions import CreatedModifiedByModelSerializer


class CountrySerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Country

        fields = (
            'id',
            'name',
            'abbreviation'
        )


class StateSerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = State

        fields = (
            'id',
            'name',
            'abbreviation'
        )
