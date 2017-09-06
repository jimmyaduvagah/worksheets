from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from django.contrib.contenttypes.models import ContentType
from action_log.models import Action


class CreatedModifiedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, blank=True, editable=False)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name="%(app_label)s_%(class)s_created_by_related")
    modified_on = models.DateTimeField(auto_now=True, blank=True, editable=False)
    modified_by = models.ForeignKey(User, null=True, blank=True, related_name="%(app_label)s_%(class)s_modified_by_related")

    # def save(self, *args, **kwargs):
    #     if not self.created_on:
    #         self.created_on = timezone.now()
    #
    #     self.modified_on = timezone.now()
    #
    #     #TODO: Make sure you handle the created/modifed users.  Probably needs to be done at the view level.
    #     return super(CreatedModifiedModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


def pathToPk(url):
    pk = None
    resolved_path = None

    if type(url) == int:
        pk = url
    else:
        if 'http://' in url or 'https://' in url:
            url = url.replace('https://','')
            url = url.replace('http://','')

            path_array = url.split('/')
            i = 0
            path = ''
            for part in path_array:
                if i > 0:
                    path = path + "/" + part
                i = i + 1
            try:
                resolved_path = resolve(path)
            except:
                return ''
            if resolved_path != None:
                pk = resolved_path.kwargs['pk']
        else:
            pk = url


    return pk

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_request_headers(request):
    headers = {}
    for field in request.META:
        if field == 'HTTP_USER_AGENT' or field == 'HTTP_REFERER' or field == 'REQUEST_METHOD' or field == 'HTTP_AUTHORIZATION' or field == 'QUERY_STRING' or field == 'CONTENT_LENGTH' or field == 'CONTENT_TYPE' or field == 'REMOTE_ADDR' or field == 'HTTP_HOST' or field == 'HTTP_ACCEPT' or field == 'SERVER_NAME' or field == 'HTTP_ACCEPT_LANGUAGE' or field == 'HTTP_ORIGIN' or field == 'HTTP_ACCEPT_ENCODING':
            headers[field] = request.META[field]

    return headers

def log_action(request, obj=None):
    data = {
        'POST': request.POST,
        'GET': request.GET
    }
    if obj == None:
        Action.objects.create(
            ip=get_client_ip(request),
            method=request.META.get('REQUEST_METHOD',''),
            endpoint=request.get_full_path(),
            user=request.user,
            headers=get_request_headers(request),
            data=data
        )
    else:
        Action.objects.create(
            ip=get_client_ip(request),
            method=request.META.get('REQUEST_METHOD',''),
            endpoint=request.get_full_path(),
            object_id=obj.pk,
            user=request.user,
            content_type=ContentType.objects.get_for_model(obj),
            headers=get_request_headers(request),
            data=data
        )

