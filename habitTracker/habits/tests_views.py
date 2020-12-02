import json
from django.http import response
from django.test import TestCase, tag, client
from django.test.client import Client
from .models import ActivityEntry, ActivityLog, DataSet, Habit, QuantitativeData, QualitativeData, QualitativeDataSet, QuantitativeDataSet,SubHabit, User, MainHabit, ViewRequest, SubHabitError
from .signals import *
from datetime import datetime
import pytz

@tag('sendRequest')
class SendRequestTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.u1 = User.objects.create(username="u1", email="u1@example.com", password="password1")
        self.u2 = User.objects.create(username="u2", email="u2@example.com", password="password1")
        self.mh1 = MainHabit.objects.create(name="AAA", owner=self.u1)

    # def test_get_correct_request(self):
    #     """ Check if the javascipt call retrives the view request """
    #     print(self.c.login(username="u1", password="password1"))
    #     jsonBody = {
    #         "from" : self.u1.username,
    #         "to" : self.u2.username,
    #         "habit" : self.mh1.id
    #     }

    #     response = self.c.post('/sendRequest', 
    #                                 json.dumps(jsonBody), 
    #                                 content_type='application/json')
    #     print(response)

    # def test_send_request(self):
    #     """ Check if a view request can be created """
    #     pass

    # def test_accept_request(self):
    #     """ Check if accepting request removes if """
    #     pass

    # def test_reject_request(self):
    #     """ Check if rejecting reqquest removes it """
    #     pass
    
