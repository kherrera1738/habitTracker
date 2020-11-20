from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from numbers import Number

import pytz

# Create your models here.
class User(AbstractUser):
    def __str__(self):
        return f"{self.username} | {self.id}"

    def changeUsername(self, newName):
        self.username = newName
        self.save()
    
    def changeEmail(self, newEmail):
        self.email = newEmail
        self.save()

    def createHabit(self, name):
        if self.habits.filter(name=name).exists():
            return False
        return Habit.objects.create(name=name, owner=self)

class Habit(models.Model):
    """ Type: 0 Quantitative, 1 Qualitiative. Defaults to Quatitative """

    name = models.CharField(max_length=60)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits")
    viewers = models.ManyToManyField(User, related_name="viewingUsers", default=None, blank=True)
    dataType = models.SmallIntegerField(default=0)

    def sendRequest(self, userId):
        if userId == self.owner.id or self.viewers.filter(id=userId).exists():
            return False
        recievingUser = User.objects.get(id=userId)
        return ViewRequest.objects.create(associatedHabit=self, recievingUser=recievingUser, sendingUser=self.owner)

    def removeViewer(self, userId):
        userToRemove = User.objects.get(id=userId)
        self.viewers.remove(userToRemove)

    def addData(self, data):
        return self.getDataSet().addData(data)

    def getDataSetType(self):
        types = {
            0: QuantitativeDataSet,
            1: QualitativeDataSet
        }

        return types[self.dataType]

    def getDataSet(self):
        return self.getDataSetType().objects.get(associatedHabit=self)

    def removeData(self, id):
        return self.getDataSet().removeData(id)

    def updateEntry(self, id, data):
        return self.getDataSet().updateEntry(id, data)

class SubHabitError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class MainHabit(Habit):

    def __str__(self):
        return f"{self.id} | Main Habit: {self.name} | {self.owner.username}"

    def createSubhabit(self, name):
        if self.subhabits.filter(name=name).exists():
            raise SubHabitError(name, f"Habit with name {name} already exists")
        sh = SubHabit.objects.create(name=name, owner=self.owner, dataType=self.dataType, mainHabit=self)
        viewers = list(self.viewers.all())
        sh.viewers.set(viewers)
        return sh

    def removeSubhabit(self, id):
        mainDataSet = self.getDataSet()
        subhabit = SubHabit.objects.get(id=id)
        entires = subhabit.getDataSet().dataEntries.all()
        entires.update(parentSet=mainDataSet)
        subhabit.delete()
        return True

    def getData(self):
        data = self.getDataSet().dataEntries.all()
        subhabits = list(self.subhabits.all())
        for subhabit in subhabits:
            data = data | subhabit.getDataSet().dataEntries.all()
        return data

    def getByDate(self, date, onlyMain=True):
        entires = self.getDataSet().getByDate(date)
        if not onlyMain:
            for subhabit in list(self.subhabits.all()):
                entires = entires | subhabit.getDataSet().getByDate(date)
        return entires

    def getByMonthAndYear(self, date, onlyMain=True):
        entires = self.getDataSet().getByMonthAndYear(date)
        if not onlyMain:
            for subhabit in list(self.subhabits.all()):
                entires = entires | subhabit.getDataSet().getByMonthAndYear(date)
        return entires
    
    def getByYear(self, date, onlyMain=True):
        entires = self.getDataSet().getByYear(date)
        if not onlyMain:
            for subhabit in list(self.subhabits.all()):
                entires = entires | subhabit.getDataSet().getByYear(date)
        return entires

    def getByDateRange(self, start, end, onlyMain=True):
        entires = self.getDataSet().getByDateRange(start, end)
        if not onlyMain:
            for subhabit in list(self.subhabits.all()):
                entires = entires | subhabit.getDataSet().getByDateRange(start, end)
        return entires
    
    def getByMonthAndYearRange(self, start, end, onlyMain=True):
        entires = self.getDataSet().getByMonthAndYearRange(start, end)
        if not onlyMain:
            for subhabit in list(self.subhabits.all()):
                entires = entires | subhabit.getDataSet().getByMonthAndYearRange(start, end)
        return entires

    def getByYearRange(self, start, end, onlyMain=True):
        entires = self.getDataSet().getByYearRange(start, end)
        if not onlyMain:
            for subhabit in list(self.subhabits.all()):
                entires = entires | subhabit.getDataSet().getByYearRange(start, end)
        return entires

    def getByFiveYear(self, start, onlyMain=True): 
        entires = self.getDataSet().getByFiveYear(start)
        if not onlyMain:
            for subhabit in list(self.subhabits.all()):
                entires = entires | subhabit.getDataSet().getByFiveYear(start)
        return entires

class SubHabit(Habit):
    mainHabit = models.ForeignKey(MainHabit, on_delete=models.CASCADE, related_name="subhabits")

    def __str__(self):
        return f"{self.id} | Sub Habit: {self.name}->{self.mainHabit.name} | {self.owner.username}"

    def getByDate(self, date):
        return self.getDataSet().getByDate(date)

    def getByMonthAndYear(self, date):
        return self.getDataSet().getByMonthAndYear(date)
    
    def getByYear(self, date):
        return self.getDataSet().getByYear(date)

    def getByDateRange(self, start, end):
        return self.getDataSet().getByDateRange(start, end)
    
    def getByMonthAndYearRange(self, start, end):
        return self.getDataSet().getByMonthAndYearRange(start, end)

    def getByYearRange(self, start, end):
        return self.getDataSet().getByYearRange(start, end)

    def getByFiveYear(self, start): 
        return self.getDataSet().getByFiveYear(start)

class ActivityLog(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="activityLog")
    limit = models.IntegerField(default=10)
    notificationCount = models.IntegerField(default=0) 

    def __str__(self):
        return f"{self.id} | {self.owner.username}: {self.notificationCount}"

    def addEntry(self, content):
        if(self.notificationCount >= self.limit):
            self.makeRoom()
        self.notificationCount += 1
        return ActivityEntry.objects.create(parentLog=self, content=content, read=False)
    
    def removeEntry(self, id):
        self.notificationCount -= 1
        entry = self.retrieve(id)
        if entry:
            entry.delete() 

    def markRead(self, id):
        entry = self.retrieve(id)
        if entry:
            entry.markRead()
            return entry

    def retrieve(self, id):
        entry = self.entries.filter(id=id) 
        if entry.all().exists():
            return entry.get()

    def makeRoom(self):
        readEntries = self.entries.filter(read=True)
        # see if there are read entries that can be deleted
        if readEntries.all().exists():
            readEntries.earliest().delete()

        # otherwise delete the oldest entry
        else:
            self.entries.earliest().delete()
        self.notificationCount -= 1

class ActivityEntry(models.Model):
    parentLog = models.ForeignKey(ActivityLog, on_delete=models.CASCADE, related_name="entries")
    content = models.CharField(max_length=300)
    read = models.BooleanField(default=False)
    createTime = models.DateTimeField(auto_now_add=True)   

    class Meta:
        get_latest_by = 'createTime'

    def __str__(self):
        return f"{self.id} | {self.parentLog.owner.username}"

    def markRead(self):
        self.read = True
        self.save()

class ViewRequest(models.Model):
    associatedHabit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="pendingRequests")
    recievingUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recievedRequests")
    sendingUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sentRequests")

    def __str__(self):
        return f"{self.id} | {self.associatedHabit.name} | ({self.sendingUser}) -> ({self.recievingUser})"

    def reject(self):
        self.delete()

    def accept(self):
        self.associatedHabit.viewers.add(self.recievingUser)
        self.delete()

class DataSet(models.Model):
    associatedHabit = models.OneToOneField(Habit, on_delete=models.CASCADE, related_name="dataSet")
    type = models.IntegerField(default=0)

    monthDays = {
        1: 31,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }

    def getByDate(self, date):
        return self.dataEntries.filter(date__year=date.year, date__month=date.month, date__day=date.day)

    def getByMonthAndYear(self, date):
        return self.dataEntries.filter(date__year=date.year, date__month=date.month)
    
    def getByYear(self, date):
        return self.dataEntries.filter(date__year=date.year)

    def getByDateRange(self, start, end):
        updatedStart = self.setStart(start)
        updatedEnd = self.setEnd(end)
        return self.dataEntries.filter(date__gte=updatedStart, date__lte=updatedEnd)
    
    def getByMonthAndYearRange(self, start, end):
        return self.getByDateRange(self.setByMonthStart(start), self.setByMonthEnd(end))

    def getByYearRange(self, start, end):
        return self.getByMonthAndYearRange(self.setByYearStart(start), self.setByYearEnd(end))

    def getByFiveYear(self, start): 
        end = datetime(year=start.year+4, month=1, day=1)
        return self.getByYearRange(self.setByYearStart(start), self.setByYearEnd(end))

    def setStart(self, start):
        return datetime(year=start.year, month=start.month, day=start.day, hour=0, minute=0, second=0, tzinfo=start.tzinfo)

    def setEnd(self, end):
        return datetime(year=end.year, month=end.month, day=end.day, hour=23, minute=59, second=59, tzinfo=end.tzinfo)

    def setByMonthStart(self, start):
        return datetime(year=start.year, month=start.month, day=1, tzinfo=start.tzinfo)

    def setByMonthEnd(self, end):
        if end.month == 2:
            day = 29 if end.year % 4 == 0 else 28
        else:
            day = self.monthDays[end.month]
        return datetime(year=end.year, month=end.month, day=day, tzinfo=end.tzinfo)

    def setByYearStart(self, start):
        return datetime(year=start.year, month=1, day=1, tzinfo=pytz.utc)

    def setByYearEnd(self, end):
        return datetime(year=end.year, month=12, day=1, tzinfo=pytz.utc)

class QualitativeDataSet(DataSet):
    def __str__(self):
        return f"{self.id} | {self.associatedHabit} | 0"

    def addData(self, data):
        if isinstance(data, str):
            return QualitativeData.objects.create(parentSet=self, content=data)
        return False

    def updateEntry(self, entryId, data):
        if isinstance(data, str):
           return QualitativeData.objects.filter(id=entryId).update(content=data)
        return 
    
    def removeData(self, entryId):
        if QualitativeData.objects.filter(id=entryId).exists():
            QualitativeData.objects.get(id=entryId).delete()
            return True
        return False

class QuantitativeDataSet(DataSet):
    def __str__(self):
        return f"{self.id} | {self.associatedHabit} | 1"
    
    def addData(self, data):
        if isinstance(data, Number):
            return QuantitativeData.objects.create(parentSet=self, content=data)
        return False

    def updateEntry(self, entryId, data):
        if isinstance(data, Number):
           return QuantitativeData.objects.filter(id=entryId).update(content=data)
        return 
    
    def removeData(self, entryId):
        if QuantitativeData.objects.filter(id=entryId).exists():
            QuantitativeData.objects.get(id=entryId).delete()
            return True
        return False

class DataEntry(models.Model):
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} | {self.parentSet.associatedHabit.name}: {self.parentSet.type}| {self.date}"

class QuantitativeData(DataEntry):
    parentSet = models.ForeignKey(QuantitativeDataSet, on_delete=models.CASCADE, related_name="dataEntries", default=None)
    content = models.DecimalField(max_digits=20, decimal_places=2)

class QualitativeData(DataEntry):
    parentSet = models.ForeignKey(QualitativeDataSet, on_delete=models.CASCADE, related_name="dataEntries", default=None)
    content = models.TextField()
