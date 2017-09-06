from django.db import models
from worksheet.utils import CreatedModifiedModel
from django.utils import timezone


class MessageManager(models.Manager):
    def do_ready_messages(self):
        import os
        import sys
        import psutil

        pid = str(os.getpid())
        pidfile = "/tmp/do_ready_messages.pid"
        pids = psutil.pids()

        if os.path.isfile(pidfile):
            print ("%s already exists" % pidfile)
            if int(file(pidfile,'r').readlines()[0]) in pids:
                print ("%s matches an existing PID %s, exiting." % (pidfile, pid))
                sys.exit()
        file(pidfile, 'w').write(pid)
        try:
            messages = self.get_queryset().filter(send_after__lt=timezone.now(), is_complete=False)
            for message in messages:
                message.do_message()
        finally:
            os.unlink(pidfile)


# Create your models here.
class Message(CreatedModifiedModel):
    objects = MessageManager()

    send_after = models.DateTimeField(null=True, blank=True)
    called_by = models.CharField(max_length=255, null=False, blank=True)
    message = models.TextField(null=False, blank=False)
    is_complete = models.BooleanField(default=False)
    completed_on = models.DateTimeField(null=True, blank=True)

    attempts = models.IntegerField(null=False, blank=False, default=0)
    attempt_status = models.TextField(blank=True)

    def __unicode__(self):
        return "Messaged Called By %s on %s" % (self.called_by, self.created_on)

    def do_message(self):
        if self.attempts < 2:
            try:
                exec (self.message)
                self.completed_on = timezone.now()
                self.is_complete = True
                self.save()
                print ("Did %s" % self)
                if self.attempt_status:
                    self.attempt_status += "\n"
                self.attempt_status += "%s - Did %s" % (timezone.now(), self)
            except Exception as inst:
                err = ""
                err += str(type(inst))
                err += "\n"
                err += str(inst)
                if self.attempt_status:
                    self.attempt_status += "\n"
                self.attempt_status += "%s - %s" % (timezone.now(), err)

            self.attempts += 1
            self.save()

    def save(self, *args, **kwargs):
        if self.called_by:
            pass
        else:
            try:
                import inspect
                curframe = inspect.currentframe()
                calframe = inspect.getouterframes(curframe, 2)
                self.called_by = calframe[1][3]
            except:
                self.called_by = "Could not determine"

        if not self.send_after:
            self.send_after = timezone.now()

        super(Message, self).save(*args, **kwargs)
