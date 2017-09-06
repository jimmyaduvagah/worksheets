__author__ = 'aduvagah'
from dbmq.models import Message
from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Runs all ready dbmq messages"

    def handle_noargs(self, **options):
        Message.objects.do_ready_messages()