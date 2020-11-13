from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, ActivityLog

@receiver(post_save, sender=User)
def createActivityLog(sender, instance, created, **kwargs):
    """ Create activity log when a User instance is made """
    if created:
        ActivityLog.objects.create(owner=instance)

class SubHabitError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message