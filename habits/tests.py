from django.test import TestCase, tag
from .models import ActivityEntry, ActivityLog, DataSet, Habit, QuantitativeData, QualitativeData, QualitativeDataSet, QuantitativeDataSet,SubHabit, User, MainHabit, ViewRequest, SubHabitError
from .signals import *
from datetime import datetime
import pytz

# Create your tests here.
@tag('User', 'rev1')
class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="U1", email="U1@exmaple.com", password="u1password")
        User.objects.create(username="U2", email="U2@exmaple.com", password="u2password")

    def test_change_username(self):
        """ check if username can be changed in model """
        u1 = User.objects.get(username="U1")
        u1.changeUsername("U1new")
        self.assertEqual(u1.username, "U1new")
    
    def test_change_email(self):
        """ check if email can be successfully updated """
        u1 = User.objects.get(username="U1")
        u1.changeEmail("U1new@example.com")
        self.assertEqual(u1.email, "U1new@example.com")

    def test_create_habit(self):
        """ create new habit associated with user """
        u1 = User.objects.get(username="U1")
        h1 = u1.createHabit("running")
        self.assertEqual(list(u1.habits.all()), list(Habit.objects.filter(id=h1.id)))

    def test_verify_AcivityLog_Creation(self):
        """ check if ActiviyLog is Successfully created """
        activityLogCount = ActivityLog.objects.all().count()
        self.assertEquals(2, activityLogCount)

    def test_accept_request(self):
        """ Check is user is on view list of habit """
        u1 = User.objects.get(username="U1")
        u2 = User.objects.get(username="U2")
        mh1 = u1.createHabit("Running")
        r1 = mh1.sendRequest(u2.id)
        r1.accept()
        self.assertTrue(mh1.viewers.filter(id=u2.id).exists())

    def test_reject_request(self):
        """ Check that request has been removed """
        u1 = User.objects.get(username="U1")
        u2 = User.objects.get(username="U2")
        mh1 = u1.createHabit("Running")
        r1 = mh1.sendRequest(u2.id)
        r1.reject()
        self.assertFalse(mh1.viewers.filter(id=u2.id).exists())

    def test_create_habit_with_same_name(self):
        """ User should not be able to create a habit with the same name """
        u1 = User.objects.get(username="U1")
        u1.createHabit("Running")
        self.assertFalse(u1.createHabit("Running"))

@tag('ActivityLog', 'rev1')
class ActivityLogTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="U1", email="U1@exmaple.com", password="u1password")
        User.objects.create(username="U2", email="U2@exmaple.com", password="u2password")

    def test_check_owner_correct(self):
        """ Check if the owner is the correct user """
        u1 = User.objects.get(username="U1")
        al1 = u1.activityLog
        self.assertEqual(al1.owner, u1)

    def test_add_entry(self):
        """ Attempt to add an entry """
        al1 = User.objects.get(username="U1").activityLog
        e1 = al1.addEntry("AAA")
        entries = al1.entries.all()
        count = entries.count()

        # Check that an entry was created
        self.assertEqual(ActivityEntry.objects.all().count(), 1)

        # Check that the user log has 1 entry
        self.assertEqual(count, 1)
        
        # Check that theyre the same entry
        self.assertEqual(list(entries), [e1])

        # Check that content is the same
        self.assertEqual(e1.content, "AAA")

        # Check that entry is unread
        self.assertFalse(e1.read)

    def test_add_multiple_entries(self):
        """ Add 5 entries and Check count"""
        al1 = User.objects.get(username="U1").activityLog
        
        for i in range(5):
            al1.addEntry(str(i))

        entries = al1.entries.all()
        count = entries.count()

        # Check that an entry was created
        self.assertEqual(ActivityEntry.objects.all().count(), 5)

        # Check that the user log has 1 entry
        self.assertEqual(count, 5)

    def test_add_multiple_different_user(self):
        """ Check multiple users can have their own entry counts """
        al1 = User.objects.get(username="U1").activityLog
        al2 = User.objects.get(username="U2").activityLog

        for i in range(3):
            al1.addEntry(str(i))

        for i in range(3):
            al2.addEntry(str(i))

        countU1 = al1.entries.all().count()
        countU2 = al2.entries.all().count()
        # Check that there are the correct total of entries
        self.assertEqual(ActivityEntry.objects.all().count(), 6)

        # Check individual entry counts
        self.assertEqual(countU1, 3)
        self.assertEqual(countU2, 3)

    def test_remove_entry(self):
        """remove an entry from a log"""
        al1 = User.objects.get(username="U1").activityLog
        e1 = al1.addEntry("AAA")

        #Check that an entry was created
        self.assertEqual(ActivityEntry.objects.all().count(), 1)

        # Check that the user log has 1 entry
        self.assertEqual(al1.entries.all().count(), 1)

        al1.removeEntry(e1.id)

        e1_id = e1.id
        # Check that entry is not in database
        self.assertFalse(al1.entries.filter(id=e1_id).exists())


    def test_mark_read(self):
        """ Mark opened entry as read """
        al1 = User.objects.get(username="U1").activityLog
        e1 = al1.addEntry("AAA")
        e1_read = al1.markRead(e1.id)
        self.assertTrue(e1_read.read)

    def test_fill_to_limit_unread(self):
        """ Add more than 10 unread entries. The oldest entry should be removed """
        al1 = User.objects.get(username="U1").activityLog
        e1_id = al1.addEntry("AAA").id
        for i in range(10):
            al1.addEntry(str(i))

        # Make sure id entry has been deleted
        self.assertFalse(ActivityEntry.objects.filter(id=e1_id).exists())
    
    def test_fill_to_limit_read(self):
        """ Add more than 10 entries with one that is read. The read one should be removed """
        al1 = User.objects.get(username="U1").activityLog
        for i in range(9):
            al1.addEntry(str(i))

        e1 = al1.addEntry("AAA")
        e1.markRead()

        e1_id = e1.id
        e2_id = al1.addEntry("BBB").id

        # Check that e1 is removed
        self.assertFalse(ActivityEntry.objects.filter(id=e1_id).exists())

        # Check that e2 is in activity log
        self.assertTrue(al1.entries.filter(id=e2_id).exists())

    def test_count_check(self):
        """ Check that counter goes up """
        al1 = User.objects.get(username="U1").activityLog
        for i in range(10):
            al1.addEntry(str(i))

        self.assertEquals(al1.notificationCount, 10)

    def test_fill_to_limit_with_other_users(self):
        """ Check that the oldest within a Activity log is being removed. Not the oldest in database """
        al2 = User.objects.get(username="U2").activityLog
        e2_id = al2.addEntry("BBB").id
        
        al1 = User.objects.get(username="U1").activityLog
        e1_id = al1.addEntry("AAA").id
        for i in range(10):
            al1.addEntry(str(i))

        # Make sure id entry has been deleted
        self.assertFalse(ActivityEntry.objects.filter(id=e1_id).exists())

        # Make sure oldest entry is still in database
        self.assertTrue(ActivityEntry.objects.filter(id=e2_id).exists())

@tag('DataSet', 'DataSetBasics', 'rev1')
class DataSetTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create(username="U1", email="U1@exmaple.com", password="u1password")
        MainHabit.objects.create(name="AAA", owner=u1, dataType=0)
        MainHabit.objects.create(name="BBB", owner=u1, dataType=1)

    def test_add_correct_data(self):
        """ Try to add correct data to corresponding dataset type """
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        de1 = d1.addData(1)
        de2 = d2.addData("A")

        self.assertEqual(de1.content, 1)
        self.assertEqual(de2.content, "A")

    def test_add_wrong_data(self):
        """ Try to add missmatched data to the wrong type of dataset """
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        self.assertFalse(d1.addData("A"))
        self.assertFalse(d2.addData(1))

    def test_update_data(self):
        """ Attempt to change data from entry """
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        de1 = d1.addData(1)
        de2 = d2.addData("A")

        d1.updateEntry(de1.id, 2)
        d2.updateEntry(de2.id, "B")

        de1.refresh_from_db()
        de2.refresh_from_db()

        self.assertEqual(de1.content, 2)
        self.assertEqual(de2.content, "B")

    def test_update_wrong_data(self):
        """ Attempt to update with wrong data type """
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        de1 = d1.addData(1)
        de2 = d2.addData("A")

        self.assertFalse(d1.updateEntry(de1.id, "B"))
        self.assertFalse(d2.updateEntry(de2.id, 2))

    def test_remove_entry(self):
        """ Attempt to remove an entry from database and set """
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        de1_id = d1.addData(1).id
        de2_id = d2.addData("A").id

        self.assertTrue(d1.removeData(de1_id))
        self.assertTrue(d2.removeData(de2_id))

        self.assertEqual(d1.dataEntries.all().count(), 0)
        self.assertEqual(d2.dataEntries.all().count(), 0)

    def test_remove_nonexistant_entry(self):
        """ Attempt to remove an entry that is not in dataset """
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        self.assertFalse(d1.removeData(1))
        self.assertFalse(d2.removeData(1))

@tag('DataSet', 'DataSetQuery', 'rev1')
class DataSetQueryCase(TestCase):
    def setUp(self):
        u1 = User.objects.create(username="U1", email="U1@exmaple.com", password="u1password")
        mh1 = MainHabit.objects.create(name="AAA", owner=u1, dataType=0)
        mh2 = MainHabit.objects.create(name="BBB", owner=u1, dataType=1)
        ds1 = mh1.getDataSet()
        ds2 = mh2.getDataSet()

        for year in range(2015, 2020): # 2015,2016,2017,2018,2019 
            for month in range(1, 12, 3): # 1,4,7,10
                for day in range(1, 12, 3): # 1,4,7,10
                    for hour in range(0, 12, 2): # 0,2,4,6,8,10
                        date = datetime(year=year, month=month, day=day, hour=hour, tzinfo=pytz.utc)
                        d1 = QuantitativeData.objects.create(parentSet=ds1, content=year*1000000+month*10000+day*10+hour)
                        d2 = QualitativeData.objects.create(parentSet=ds2, content=str(year)+str(month)+str(day)+str(hour))
                        d1.date = date
                        d1.save()
                        d2.date = date
                        d2.save()

    def test_get_data_by_specific_date(self):
        """ Get data from a given date """
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        year = 2015
        month = 1
        day = 1

        date = datetime(year=year, month=month, day=day)

        results1 = d1.getByDate(date)
        results2 = d2.getByDate(date)

        self.assertEqual(results1.all().count(), 6)
        self.assertEqual(results2.all().count(), 6)

        for hour in range(0, 12, 2):
            self.assertTrue(results1.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())
            self.assertTrue(results2.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())

    def test_get_data_by_month_and_year(self):
        """ Get data from a given month """
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        year = 2015
        month = 1
        day = 1

        date = datetime(year=year, month=month, day=day)

        results1 = d1.getByMonthAndYear(date)
        results2 = d2.getByMonthAndYear(date)

        self.assertEqual(results1.all().count(), 24)
        self.assertEqual(results2.all().count(), 24)
        for day in range(1, 12, 3):
            for hour in range(0, 12, 2):
                self.assertTrue(results1.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())
                self.assertTrue(results2.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())

    def test_get_data_by_year(self):
        """ Get Data from a given year """
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        year = 2015
        month = 1
        day = 1

        date = datetime(year=year, month=month, day=day)

        results1 = d1.getByYear(date)
        results2 = d2.getByYear(date)

        self.assertEqual(results1.all().count(), 96)
        self.assertEqual(results2.all().count(), 96)
        for month in range(1, 12, 3):
            for day in range(1, 12, 3):
                for hour in range(0, 12, 2):
                    self.assertTrue(results1.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())
                    self.assertTrue(results2.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())

    def test_get_data_from_date_range(self):
        """ Get data between two date ranges """
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        yearStart = 2015
        monthStart = 1
        dayStart = 1

        yearEnd = 2016
        monthEnd = 10
        dayEnd = 10
        
        startDate = datetime(year=yearStart, month=monthStart, day=dayStart, tzinfo=pytz.utc)
        endDate = datetime(year=yearEnd, month=monthEnd, day=dayEnd, tzinfo=pytz.utc)

        results1 = d1.getByDateRange(startDate, endDate)
        results2 = d2.getByDateRange(startDate, endDate)

        self.assertEqual(results1.all().count(), 192)
        self.assertEqual(results2.all().count(), 192)
        for year in range(2015, 2017):
            for month in range(1, 12, 3):
                for day in range(1, 12, 3):
                    for hour in range(0, 12, 2):
                        self.assertTrue(results1.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())
                        self.assertTrue(results2.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())
    
    def test_get_data_from_month_and_year_range(self):
        """ Get data between two months and years"""
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        year = 2015
        monthStart = 1
        monthEnd = 7
        
        startDate = datetime(year=year, month=monthStart, day=1, tzinfo=pytz.utc)
        endDate = datetime(year=year, month=monthEnd, day=1, tzinfo=pytz.utc)

        results1 = d1.getByMonthAndYearRange(startDate, endDate)
        results2 = d2.getByMonthAndYearRange(startDate, endDate)

        self.assertEqual(results1.all().count(), 72)
        self.assertEqual(results2.all().count(), 72)
        for month in range(1, 8, 3):
            for day in range(1, 12, 3):
                for hour in range(0, 12, 2):
                    self.assertTrue(results1.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())
                    self.assertTrue(results2.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())
    
    def test_get_data_5_year_range(self):
        """ Get data from a 5 year range """
        d1 = QuantitativeDataSet.objects.get(type=0)
        d2 = QualitativeDataSet.objects.get(type=1)

        startYear = 2015
        
        startDate = datetime(year=startYear, month=1, day=1, tzinfo=pytz.utc)

        results1 = d1.getByFiveYear(startDate)
        results2 = d2.getByFiveYear(startDate)

        self.assertEqual(results1.all().count(), 480)
        self.assertEqual(results2.all().count(), 480)
        for year in range(2015,2020):
            for month in range(1, 8, 3):
                for day in range(1, 12, 3):
                    for hour in range(0, 12, 2):
                        self.assertTrue(results1.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())
                        self.assertTrue(results2.filter(date__year=year, date__month=month, date__day=day, date__hour=hour).exists())        

    # def test_get_data_by_day_of_week(self):
    #     """ Get data that occurs on a given day of the week reguardless of month and year """
    #     pass

    # def test_get_data_by_month_of_year(self):
    #     """ Get data that occurs on a given month of the year reguardless of year """
    #     pass

@tag('ViewRequest', 'rev1')
class ViewRequestTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create(username="U1", email="U1@exmaple.com", password="u1password")
        u2 = User.objects.create(username="U2", email="U2@exmaple.com", password="u2password")
        mh1 = MainHabit.objects.create(name="Running", owner=u1)
        ViewRequest.objects.create(associatedHabit=mh1, recievingUser=u2, sendingUser=u1)

    def test_request_sender_and_reciever_correct(self):
        """ Check if request data has correct to, from, and hhabit data """
        u1 = User.objects.get(username="U1")
        u2 = User.objects.get(username="U2")
        mh1 = MainHabit.objects.get(name="Running") 
        r1 = ViewRequest.objects.get(associatedHabit=mh1)

        # Make sure sending user can see that request has been sent
        self.assertEqual(u1.sentRequests.all().count(), 1)
        self.assertEqual(u1.sentRequests.get(), r1)

        # Make sure that 
        self.assertEqual(u2.recievedRequests.all().count(), 1)
        self.assertEqual(u2.recievedRequests.get(), r1)

        # Make sure that habit has pending request
        self.assertEqual(mh1.pendingRequests.all().count(), 1)
        self.assertEqual(mh1.pendingRequests.get(), r1)

    def test_self_rejected(self):
        """ Check that request is deleted if rejected """
        u1 = User.objects.get(username="U1")
        mh1 = MainHabit.objects.get(name="Running") 
        r1 = ViewRequest.objects.get(associatedHabit=mh1)
        r1_id = r1.id
        r1.reject()

        # Make sure request was removed
        self.assertFalse(ViewRequest.objects.filter(id=r1_id).exists())

        # Make sure that the view list is not updated
        self.assertFalse(mh1.viewers.filter(id=u1.id).exists())

    def test_self_accepted(self):
        """ Check that request adds User to view list """
        u2 = User.objects.get(username="U2")
        mh1 = MainHabit.objects.get(name="Running") 
        r1 = ViewRequest.objects.get(associatedHabit=mh1)
        r1_id = r1.id
        r1.accept()

        # Make sure request was removed
        self.assertFalse(ViewRequest.objects.filter(id=r1_id).exists())

        # Make sure that the view list is updated
        self.assertTrue(mh1.viewers.filter(id=u2.id).exists())

@tag('Habit', 'rev1')
class HabitTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create(username="U1", email="U1@exmaple.com", password="u1password")
        User.objects.create(username="U2", email="U2@exmaple.com", password="u2password")
        MainHabit.objects.create(name="AAA", owner=u1)

    def test_owner_correct(self):
        """ Check that the owner is correctly added """
        u1 = User.objects.get(username="U1")
        mh1 = MainHabit.objects.get(name="AAA")
        self.assertEqual(mh1.owner, u1)

    def test_send_request(self):
        """ Attempt to send a view request """
        u1 = User.objects.get(username="U1")
        u2 = User.objects.get(username="U2")
        mh1 = MainHabit.objects.get(name="AAA")
        r1 = mh1.sendRequest(u2.id)
        self.assertEqual(r1.associatedHabit, mh1)
        self.assertEqual(r1.recievingUser, u2)
        self.assertEqual(r1.sendingUser, u1)

    def test_rejected_request(self):
        """ Check if request is deleted if rejected """
        u2 = User.objects.get(username="U2")
        mh1 = MainHabit.objects.get(name="AAA")
        r1 = mh1.sendRequest(u2.id)
        r1_id = r1.id
        r1.reject()
        self.assertFalse(ViewRequest.objects.filter(id=r1_id).exists())

    def test_accepted_request(self):
        """ Check if user has been added to view list """
        u2 = User.objects.get(username="U2")
        mh1 = MainHabit.objects.get(name="AAA")
        r1 = mh1.sendRequest(u2.id)
        r1_id = r1.id
        r1.accept()
        self.assertFalse(ViewRequest.objects.filter(id=r1_id).exists())
        self.assertTrue(mh1.viewers.filter(id=u2.id).exists())

    def test_remove_from_view_list(self):
        """ Check that a user can be take off of view list """
        u2 = User.objects.get(username="U2")
        mh1 = MainHabit.objects.get(name="AAA")
        mh1.viewers.add(u2)
        mh1.removeViewer(u2.id)
        self.assertFalse(mh1.viewers.filter(id=u2.id).exists())

    def test_dataset_created(self):
        """ Check that correct dataset is made """
        mh1 = MainHabit.objects.get(name="AAA")
        self.assertTrue(DataSet.objects.filter(associatedHabit=mh1).exists())

    def test_cannot_send_request_to_owner(self):
        """ Check that you cannot send request to owner """
        u1 = User.objects.get(username="U1")
        mh1 = MainHabit.objects.get(name="AAA")
        self.assertFalse(mh1.sendRequest(u1.id))
        self.assertFalse(ViewRequest.objects.filter(recievingUser=u1).exists())

    def test_cannot_send_request_to_someone_on_viewlist(self):
        """ Check that you cannot send a request to a user already on the view list """
        u2 = User.objects.get(username="U2")
        mh1 = MainHabit.objects.get(name="AAA")
        mh1.viewers.add(u2)
        self.assertFalse(mh1.sendRequest(u2.id))
        self.assertFalse(ViewRequest.objects.filter(recievingUser=u2).exists())

@tag('SubHabit', 'rev1')
class SubHabitTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create(username="U1", email="U1@exmaple.com", password="u1password")
        mh1 = MainHabit.objects.create(name="AAA", owner=u1)
        SubHabit.objects.create(name="CCC", owner=u1, mainHabit=mh1)

    def test_check_main_habit(self):
        """ Check main habit is correct """
        mh1 = MainHabit.objects.get(name="AAA")
        sb1 = SubHabit.objects.get(name="CCC")
        self.assertEqual(sb1.mainHabit, mh1)

    def test_add_data_entry(self):
        """ Attempt to add a data entry """
        sb1 = SubHabit.objects.get(name="CCC")
        for i in range(5):
            self.assertTrue(sb1.addData(i))
        self.assertEqual(sb1.getDataSet().dataEntries.all().count(), 5)
        self.assertTrue(sb1.getDataSet().dataEntries.filter(content=4).exists())

    def test_remove_data_entry(self):
        """ Attempt to remove a data entry """
        sb1 = SubHabit.objects.get(name="CCC")
        for i in range(5):
            self.assertTrue(sb1.addData(i))
        fifthEntryId = QuantitativeData.objects.get(content=4).id
        sb1.removeData(fifthEntryId)
        self.assertFalse(sb1.getDataSet().dataEntries.filter(id=fifthEntryId).exists())

    def test_update_data_entry(self):
        """ Update an existing entry """
        sb1 = SubHabit.objects.get(name="CCC")
        entry = sb1.addData(1)
        self.assertTrue(sb1.updateEntry(entry.id, 2))
        entry.refresh_from_db()
        self.assertEqual(entry.content, 2) 

@tag('MainHabit', 'rev1')
class MainHabitTestCase(TestCase):
    def setUp(self):
        u1 = User.objects.create(username="U1", email="U1@exmaple.com", password="u1password")
        User.objects.create(username="U2", email="U2@exmaple.com", password="u2password")
        MainHabit.objects.create(name="AAA", owner=u1)
    
    def test_owner_correct(self):
        """ Check that the owner value is correct """
        u1 = User.objects.get(username="U1")
        h1 = MainHabit.objects.get(name="AAA")
        self.assertEqual(h1.owner, u1)

    def test_create_subhabit(self):
        """ Check that subhabits can be created """
        h1 = MainHabit.objects.get(name="AAA")
        h1.createSubhabit("BBB")
        self.assertTrue(SubHabit.objects.filter(name="BBB").exists())
        self.assertTrue(h1.subhabits.exists())

    # def test_create_subhabit_wrong_type(self):
    #     """ Attempt to add a subhabit with the wrong data type """
    #     with self.assertRaisesMessage(SubhabitError, 'Tried to create Qualitative subhabit under Quanitiative habit'):
    #         SubHabit.objects.create()

    def test_subhabit_inherits_viewers_list(self):
        """ Check that a subhabit inherits the viewers list from the Main Habit """
        mh1 = MainHabit.objects.get(name="AAA")
        u2 = User.objects.get(username="U2")
        mh1.viewers.add(u2)
        sbh1 = mh1.createSubhabit("CCC")
        self.assertTrue(sbh1.viewers.filter(username="U2").exists())

    def test_remove_subhabit(self):
        """ Check that a subhabit is deleted and subhabit data is added to main habit data set """
        u1 = User.objects.get(username="U1")
        mh1 = MainHabit.objects.get(name="AAA")
        sb1 = SubHabit.objects.create(name="CCC", owner=u1, mainHabit=mh1)
        for i in range(5):
            sb1.addData(i)
        mh1.removeSubhabit(sb1.id)
        sb1_id = sb1.id
        self.assertFalse(SubHabit.objects.filter(id=sb1_id).exists())
        self.assertEquals(mh1.getDataSet().dataEntries.all().count(), 5)

    def test_get_subhabit_data(self):
        """ Check that subhabit data is included in all habit data """
        u1 = User.objects.get(username="U1")
        mh1 = MainHabit.objects.get(name="AAA")
        sb1 = SubHabit.objects.create(name="CCC", owner=u1, mainHabit=mh1)
        for i in range(5):
            sb1.addData(2*i)
            mh1.addData(2*i+1)
        self.assertEqual(mh1.getData().all().count(), 10)

    def test_create_subhabit_with_same_name(self):
        """ User should not be able to create a subhabit with the same name """
        mh1 = MainHabit.objects.get(name="AAA")
        mh1.createSubhabit("CCC")
        with self.assertRaises(SubHabitError, msg='Habit with name CCC already exists'):
            mh1.createSubhabit("CCC")
        
    def test_subhabit_gets_mainhabit_type(self):
        """ Check that adding a sub habit gives it the same datatype """
        u1 = User.objects.get(username="U1")
        mh1 = MainHabit.objects.create(name="DDD", owner=u1, dataType=1)
        sh1 = mh1.createSubhabit("CCC")
        self.assertEqual(sh1.dataType, 1)