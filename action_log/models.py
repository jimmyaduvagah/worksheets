from django.db import models

# Create your models here.
import datetime
import collections
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from jsonfield import JSONField

class Action(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)

    name = models.CharField(max_length=100, default='Action', null=False, blank=False, db_index=True)
    method = models.CharField(max_length=10, default="", null=False, blank=True, db_index=True)
    ip = models.CharField(max_length=100, null=False, blank=False, db_index=True)
    endpoint = models.TextField(null=False, blank=False, db_index=True)
    date = models.DateTimeField(default=datetime.datetime.utcnow, null=False, blank=False)
    object_id = models.PositiveIntegerField(default=None, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, default=None, null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    headers = JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, null=True, blank=True)
    data = JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict}, null=True, blank=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.user, self.name, self.endpoint,)

# objects = Action.objects.all()
# for obj in objects:
#     print 'fixing id: %s' % (obj.pk,)
#     if obj.headers != None:
#         obj.method = obj.headers['REQUEST_METHOD']
#         obj.save()
