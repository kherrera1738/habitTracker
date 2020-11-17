from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, ActivityLog, MainHabit, SubHabit, QuantitativeDataSet, QualitativeDataSet

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
        if instance.dataType == 0:
            QuantitativeDataSet.objects.create(associatedHabit=instance, type=0)
        else:
            QualitativeDataSet.objects.create(associatedHabit=instance, type=1)

class SubHabitError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message