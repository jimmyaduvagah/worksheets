from .models import Company
from rest_framework import serializers
from time_stream_api.rest_extensions import CreatedModifiedByModelSerializer


class CompanySerializer(CreatedModifiedByModelSerializer):
    class Meta:
        model = Company
        # fields = (
        #     'id',
        #     'user',
        #     'project',
        #     'name',
        #     'description',
        #     'work_day_hours',
        #     'overtime_enabled',
        # )