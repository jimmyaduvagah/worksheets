from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import UserProfile
from companies.serializers import CompanySerializer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile

        exclude = ('user', )

    is_approver = serializers.ReadOnlyField()
    user_id = serializers.IntegerField(read_only=True, source='user.id')
    user_image = serializers.ImageField(allow_empty_file=True, use_url=False, read_only=True)


class UserProfileMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user_image', )

    user_image = serializers.ImageField(allow_empty_file=True, use_url=False, read_only=True)


class UserProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile

        exclude = ('user',)

    is_approver = serializers.BooleanField(default=False)
    user_id = serializers.IntegerField(read_only=False)
    user_image = serializers.ImageField(allow_empty_file=True, use_url=False, read_only=True)


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ('pk', 'url', 'username', 'first_name', 'last_name', 'email', 'groups', 'userprofile',)


class ApproverSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class UserMiniWithImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'userprofile')

    userprofile = UserProfileMiniSerializer(many=False, read_only=True)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')



