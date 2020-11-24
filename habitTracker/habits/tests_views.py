from django.test import TestCase, tag, client
from .models import ActivityEntry, ActivityLog, DataSet, Habit, QuantitativeData, QualitativeData, QualitativeDataSet, QuantitativeDataSet,SubHabit, User, MainHabit, ViewRequest, SubHabitError
from .util import *
from datetime import datetime
import pytz

class UserUITestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username="u1", email="u1@example.com", password="password1")
        user.save()
        
    
