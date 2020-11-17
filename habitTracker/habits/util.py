from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DataSet, User, ActivityLog, MainHabit, SubHabit, Habit

@receiver(post_save, sender=User)
def createActivityLog(sender, instance, created, **kwargs):
    """ Create activity log when a User instance is made """
    if created:
        ActivityLog.objects.create(owner=instance)

@receiver(post_save, sender=MainHabit)
@receiver(post_save, sender=SubHabit)
def createDataSet(sender, instance, created, **kwargs):
    """ Create data set for each habit """
    if created:
        DataSet.objects.create(associatedHabit=instance, type=instance.dataType)

class SubHabitError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message