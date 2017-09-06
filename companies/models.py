from django.db import models
from worksheet.utils import CreatedModifiedModel
from django.contrib.auth.models import User


class Company(CreatedModifiedModel):
    name = models.CharField(max_length=255, null=False, blank=False)

    def __unicode__(self):
        return self.name
