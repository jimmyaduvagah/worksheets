from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
import requests

from .models import UserProfile


# Register your models here.
# which acts a bit like a singleton
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'UserProfiles'
    # classes = ('grp-collapse grp-open',)
    inline_classes = ('grp-collapse grp-open',)


# Define a new User admin
class UserAdminWithProfile(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
    'username', 'email', 'first_name', 'last_name', 'is_staff', 'password', 'last_login', 'date_joined', 'user_country')

    actions = ['reset_password']

    def user_country(self, obj):
        return obj.userprofile.address_country

    def reset_password(self, request, queryset):
        reset_password_url = 'https://api-timestream.prospect33.com/api/v1/rest-auth/password/reset/'
        rows_updated = 0
        for user in queryset:
            requests.post(reset_password_url, {'email': user.email})
            rows_updated += 1

        if rows_updated == 1:
            message_bit = "1 user had its"
        else:
            message_bit = "%s users had their" % rows_updated
        self.message_user(request, "%s password reset" % message_bit)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdminWithProfile)