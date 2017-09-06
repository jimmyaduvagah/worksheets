from django.contrib import admin
from .models import Action
# Register your models here.

class ActionAdmin(admin.ModelAdmin):
    ordering = ('-date',)
    list_display = ('user', 'name', 'method', 'endpoint', 'date', 'content_object',)
    change_list_filter_template = "admin/filter_listing.html"
    list_filter = ('user','endpoint', 'date', 'method')
    search_fields = ('endpoint', 'date',)


admin.site.register(Action, ActionAdmin)
