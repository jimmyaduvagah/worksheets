import time
import os
import base64
import django_filters

from django.core.files import File
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import PermissionDenied, NotAcceptable
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import permissions
from rest_framework import status
from rest_framework import renderers
from rest_framework import viewsets, filters
from rest_framework.views import APIView

from time_stream_api.utils import get_client_ip, get_request_headers
from cms_locations.models import Country, State

from .models import UserProfile
from .permissions import IsAllowedOrSuperuser
from .serializers import UserSerializer, GroupSerializer, UserProfileSerializer, UserProfileCreateSerializer
from worksheet.utils import log_action
from worksheet.settings import MEDIA_ROOT
import random


class CustomObtainAuthToken(ObtainAuthToken):

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.last_login = timezone.now()
        user.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class LogoutViewSet(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request,):
        Token.objects.get(user=request.user).delete()
        return Response({'detail': 'logged out'})


# from .models import Snippet
def codegenerator():
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pw_length = 8
    mypw = ""

    for i in range(pw_length):
        next_index = random.randrange(len(alphabet))
        mypw = mypw + alphabet[next_index]
    return mypw

class UserFilter(django_filters.FilterSet):

    class Meta:
        model = User
        fields = ['username', 'first_name','last_name', 'email', ]


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the users in the system.

    ###create_user: __/create_user/__ ###

    Allows an is_staff user to push new users into the system.

    The system attempts to match the string entry of address_country and address_state against the full name and abbreviations and replaces it with the corresponding foreign key.

    Example JSONbody for request:

        {
            "user": {
                "first_name": "Johnny",
                "last_name": "Appleseed",
                "username": "johnny.appleseed3",
                "email": "johnny.appleseed@prospect33.com"
            },
            "userprofile": {
                "phone_number": "555-123-1234",
                "address_line_1": "123 Fake st",
                "address_line_2": "",
                "address_line_3": "",
                "address_line_4": "",
                "address_city": "Faketown",
                "address_zip": "12345",
                "address_state": "virginia",
                "address_country": "united states"
            }
        }

    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    filter_class = UserFilter
    search_fields = ('username', 'first_name','last_name', 'email')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint presents the users in the system.

    ###create_user: __/create_user/__ ###

    Allows an is_staff user to push new users into the system.

    The system attempts to match the string entry of address_country and address_state against the full name and abbreviations and replaces it with the corresponding foreign key.

    Example JSONbody for request:

        {
            "user": {
                "first_name": "Johnny",
                "last_name": "Appleseed",
                "username": "johnny.appleseed3",
                "email": "johnny.appleseed@prospect33.com"
            },
            "userprofile": {
                "phone_number": "555-123-1234",
                "address_line_1": "123 Fake st",
                "address_line_2": "",
                "address_line_3": "",
                "address_line_4": "",
                "address_city": "Faketown",
                "address_zip": "12345",
                "address_state": "virginia",
                "address_country": "united states"
            }
        }

    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    filter_class = UserFilter
    search_fields = ('username', 'first_name','last_name', 'email')

    @list_route(methods=['get'])
    def current_user(self, request):

        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=request.user.pk)
        user.last_login = timezone.now()
        user.save()
        log_action(request, user)
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['post'])
    def create_user(self, request):

        if request.user.is_staff:
            print(request.data)
            request.data['user']['groups'] = dict()
            address_country = request.data['userprofile']['address_country']
            address_country = address_country.upper()

            if address_country == '':
                address_country = 'US'

            if address_country != '':

                if address_country == 'USA' or address_country == 'U.S.A':
                    address_country = 'US'

                if address_country == 'UK' or address_country == 'U.K.' or address_country == 'UNITED KINGDOM':
                    address_country = 'GB'

                address_country = Country.objects.filter(
                    Q(abbreviation__iexact=address_country)
                    | Q(name__iexact=address_country)
                ).distinct()

                if len(address_country) > 0:
                    address_country = address_country[0].pk

                request.data['userprofile']['address_country'] = address_country

            # request.data['userprofile']['is_approver'] = False

            user_serializer = UserSerializer(data=request.data['user'])
            user_serializer.is_valid(raise_exception=True)

            user_obj = user_serializer.save()

            user_obj.set_password(codegenerator())
            user_obj.save()

            if user_obj:
                request.data['userprofile']['user'] = user_obj
                request.data['userprofile']['user_id'] = user_obj.pk
                user_profile_serializer = UserProfileCreateSerializer(data=request.data['userprofile'])
                user_profile_serializer.is_valid(raise_exception=True)

                if user_profile_serializer.save():
                    log_action(request, user_obj)
                    return Response({"details":"created","object_id":user_obj.pk}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"details":"not created"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({"details":"not created"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        else:
            raise PermissionDenied('You do not have permission to perform this action.')

    @list_route(methods=['post'])
    def deactivate_user(self, request):

        if request.user.is_staff:
            print(request.data)
            user_id = request.data['user_id']
            user = User.objects.get(id=user_id)
            if user is None:
                return Response({"details": "Could not deactivate user account."}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                user.is_active = False
                user.save()
                return Response({"details": "User account has been deactivated."}, status=status.HTTP_200_OK)

        else:
            raise PermissionDenied('You do not have permission to perform this action.')

    @list_route(methods=['post'])
    def activate_user(self, request):

        if request.user.is_staff:
            print(request.data)
            user_id = request.data['user_id']
            user = User.objects.get(id=user_id)
            if user is None:
                return Response({"details": "Could not activate user account."}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                user.is_active = True
                user.save()
                return Response({"details": "User account has been activated."}, status=status.HTTP_200_OK)

        else:
            raise PermissionDenied('You do not have permission to perform this action.')





class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint presents the groups in the system.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticated,)


class UserProfilesViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the user profiles in the system.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,IsAllowedOrSuperuser)

    def list(self, request, *args, **kwargs):

        if request.user.is_staff or request.user.is_superuser:
            pass
        else:
            raise PermissionDenied('You do not have permission to access resource.')

        log_action(request)

        response = super(UserProfilesViewSet, self).list(self, request, *args, **kwargs)

        return response

    def create(self, request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            self.serializer_class = UserProfileCreateSerializer
        else:
            raise PermissionDenied('You do not have permission to access resource.')

        return super(UserProfilesViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            self.serializer_class = UserProfileCreateSerializer
        else:
            raise PermissionDenied('You do not have permission to access resource.')

        return super(UserProfilesViewSet, self).update(request, *args, **kwargs)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    This endpoint presents the user profiles in the system.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated, IsAllowedOrSuperuser)

    def list(self, request):
        queryset = self.queryset.filter()

        if request.user.pk != None:
            if request.user.userprofile != None:
                queryset = queryset.filter(pk=request.user.userprofile.pk)[0]
        else:
            raise NotAcceptable('No user profile for the current user exists.')

        log_action(request, queryset)

        serializer = self.serializer_class(queryset, many=False, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['post'], permission_classes=[IsAllowedOrSuperuser])
    def upload_user_image(self, request, pk=None):
        response = '{"details":"Accepted"}'

        image = request.FILES.get('user_image')

        if image == None:
            raise Exception

        if image != None:
            obj = UserProfile.objects.get(pk=1)
            obj.user_image = image
            obj.save()

       # log_action(request, obj)

        return Response(response)

    @detail_route(methods=['post'], permission_classes=[IsAllowedOrSuperuser])
    def upload_user_image_from_desktop(self, request, pk=None):
        response = '{"details":"Accepted"}'
        print("upload")
        data = request.body
        data = data.split(",")
        mime = data[0].split(';')[0]
        print(mime)
        data = data[1]
        if mime.find('image/') == -1:
            raise NotAcceptable

        extension = ''
        if not mime.lower().find('image/jpeg') == -1:
            extension = 'jpg'
        if not mime.lower().find('image/png') == -1:
            extension = 'png'
        if not mime.lower().find('image/gif') == -1:
            extension = 'gif'

        if data != '':
            image_file_name = "%s/user_%s.%s" % (MEDIA_ROOT, request.user.pk, extension)
            image = base64.b64decode(data);
            if os.path.isfile(image_file_name):
                image_file_name = "%s/user_%s_%s.%s" % (MEDIA_ROOT, request.user.pk, int(time.time()), extension)
            f = open(image_file_name, "w")
            f.write(image)
            f.close()

            f = open(image_file_name, "r")
            obj = UserProfile.objects.get(pk=pk)
            obj.user_image = File(f)
            obj.save()
            f.close()
            os.remove(image_file_name)

        return Response(response)
