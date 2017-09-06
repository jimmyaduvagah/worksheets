from django.contrib import admin
from .models import Message
from django.utils import timezone

class MessageAdmin(admin.ModelAdmin):
    def do_ready_messages(self, request, queryset):
        for message in queryset.filter(send_after__lt=timezone.now(), is_complete=False):
            message.do_message()

    list_display = ('__unicode__', 'send_after','is_complete','completed_on', 'attempts')
    search_fields = ('message',)
    actions = [do_ready_messages]
    list_filter = ('send_after', 'is_complete', 'attempts')


admin.site.register(Message, MessageAdmin)
