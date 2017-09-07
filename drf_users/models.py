from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    is_approver = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    address_country = models.ForeignKey('cms_locations.Country', null=True, blank=True, on_delete=models.SET_NULL)
    sick_days_per_year = models.IntegerField(null=False, blank=False, default=5)

    user_image = models.FileField(null=True, blank=True, upload_to='profile_images/')

    def __unicode__(self):
        return u"%s's profile" % self.user
