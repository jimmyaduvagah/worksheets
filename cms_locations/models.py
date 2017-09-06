from django.db import models
from worksheet.utils import CreatedModifiedModel


class CountryManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Country(CreatedModifiedModel):

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    name = models.CharField(max_length=255, null=False, blank=False, db_index=True)
    abbreviation = models.CharField(max_length=3, null=False, blank=False, db_index=True)

    def natural_key(self):
        return self.name

    def __unicode__(self):
        return self.name


class State(CreatedModifiedModel):

    class Meta:
        verbose_name = 'State'
        verbose_name_plural = 'States'

    name = models.CharField(max_length=255, null=False, blank=False, db_index=True)
    abbreviation = models.CharField(max_length=3, null=False, blank=False, db_index=True)
    country = models.ForeignKey('cms_locations.Country', null=False, blank=False, db_index=True)

    def natural_key(self):
        return self.name

    def __unicode__(self):
        return self.name



