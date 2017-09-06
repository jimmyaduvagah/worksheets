from __future__ import unicode_literals
from django.db import models
from rest_framework.compat import (
    postgres_fields,
    unicode_to_repr,
    DurationField as ModelDurationField,
)
from rest_framework.utils import model_meta
from rest_framework.utils.field_mapping import (
    get_url_kwargs, get_field_kwargs,
    get_relation_kwargs, get_nested_relation_kwargs,
    ClassLookupDict
)
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer, raise_errors_on_nested_writes, ReadOnlyField
from rest_framework.response import Response
from rest_framework import status, pagination
import base64
from django.contrib.auth import authenticate
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, HTTP_HEADER_ENCODING
from rest_framework.authtoken.models import Token
from rest_framework.compat import get_user_model
from rest_framework.authentication import BaseAuthentication, get_authorization_header


class LimitOffsetPagination(pagination.LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response({
            'state' : {
                'next_offset': self.get_next_offset(),
                'prev_offset': self.get_prev_offset(),
                'limit': self.limit,
                'total': self.count
            },
            'results': data,
        })

    def get_next_offset(self):
        return self.offset + self.limit

    def get_prev_offset(self):
        prev_offset = self.offset - self.limit
        if self.offset == 0:
            return None
        elif prev_offset < 0:
            return 0
        else:
            return prev_offset




class ReadOnlyUserField(ReadOnlyField):
    def to_representation(self, obj):
        return obj.pk

    def to_internal_value(self, data):
        return False


class ReadOnlyChoiceDisplay(ReadOnlyField):
    choices = dict()
    def __init__(self, choices=tuple(), **kwargs):
        kwargs['read_only'] = True
        if len(choices) > 0:
            self.choices = dict(choices)

        super(ReadOnlyChoiceDisplay, self).__init__(**kwargs)

    def to_representation(self, obj):
        return self.choices.get(obj,obj)

    def to_internal_value(self, data):
        return False


class IsSuperUserMixin(object):
    def is_super(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def is_super_or_admin(self, request):
        if request.user.is_superuser or request.user.userprofile.is_admin:
            return True
        else:
            return False


class CreatedModifiedByCreateModelMixin(IsSuperUserMixin):
    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, request=request)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, request):
        serializer.save(request=request)

    def perform_update(self, serializer, request):
        serializer.save(request=request)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer, request=request)
        return Response(serializer.data)


class CreatedModifiedByModelSerializer(ModelSerializer):

    modified_on = ReadOnlyField()
    created_on = ReadOnlyField()
    modified_by = ReadOnlyUserField()
    created_by = ReadOnlyUserField()


    def save(self, request, **kwargs):
        assert not hasattr(self, 'save_object'), (
            'Serializer `%s.%s` has old-style version 2 `.save_object()` '
            'that is no longer compatible with REST framework 3. '
            'Use the new-style `.create()` and `.update()` methods instead.' %
            (self.__class__.__module__, self.__class__.__name__)
        )

        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.save()`.'
        )

        assert not self.errors, (
            'You cannot call `.save()` on a serializer with invalid data.'
        )

        validated_data = dict(
            list(self.validated_data.items()) +
            list(kwargs.items())
        )

        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data, request=request)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
        else:
            self.instance = self.create(validated_data, request=request)

            assert self.instance is not None, (
                '`create()` did not return an object instance.'
            )

        return self.instance


    def create(self, validated_data, request):
        validated_data['created_by'] = request.user
        validated_data['modified_by'] = request.user

        instance = super(CreatedModifiedByModelSerializer, self).create(validated_data)

        return instance

    def update(self, instance, validated_data, request):
        validated_data['modified_by'] = request.user

        instance = super(CreatedModifiedByModelSerializer, self).update(instance, validated_data)


        return instance


class CreatedModifiedByHyperlinkedModelSerializer(CreatedModifiedByModelSerializer, HyperlinkedModelSerializer):
    pass


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    model = Token
    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            if request.GET.get('token', None):
                auth = ["Token", request.GET.get('token')]

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(auth[1])

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.select_related('user').get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)

    def authenticate_header(self, request):
        return 'Token'


