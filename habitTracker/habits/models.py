from django.db import models
from django.contrib.auth.models import AbstractUser

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

class MainHabit(Habit):

    def __str__(self):
        return f"{self.id} | Main Habit: {self.name} | {self.owner.username}"

class SubHabit(Habit):
    mainHabit = models.ForeignKey(MainHabit, on_delete=models.CASCADE, related_name="subhabits")

    def __str__(self):
        return f"{self.id} | Sub Habit: {self.name}->{self.mainHabit.name} | {self.owner.username}"

class ActivityLog(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="activityLog")
    limit = models.IntegerField(default=10)
    notificationCount = models.IntegerField(default=0) 

    def __str__(self):
        return f"{self.id} | {self.owner.name}: {self.notificationCount}"

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

    def __str__(self):
        return f"{self.id} | {self.associatedHabit} | {self.type}"

    def addData(self, data):
        if self.type == 0 and isinstance(data, int):
            return QuantitativeData.objects.create(parentSet=self, content=data)
        elif self.type == 1 and isinstance(data, str):
            return QualitiativeData.objects.create(parentSet=self, content=data)
        else:
            return False
    
    def updateEntry(self, entryId, data):
        if self.type == 0 and isinstance(data, int):
            toUpdate = QuantitativeData.objects.filter(id=entryId)
        elif self.type == 1 and isinstance(data, str):
            toUpdate = QualitiativeData.objects.filter(id=entryId)
        else:
            return False

        return toUpdate.update(content=data)

    def removeData(self, entryId):
        if self.type == 0 and QuantitativeData.objects.filter(id=entryId).exists():
            QuantitativeData.objects.get(id=entryId).delete()
            return True
        elif self.type == 1 and QualitiativeData.objects.filter(id=entryId).exists():
            QualitiativeData.objects.get(id=entryId).delete()
            return True
        else:
            return False

class DataEntry(models.Model):
    parentSet = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name="dataEntries")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} | {self.parentSet.associatedHabit.name}: {self.parentSet.type}| {self.date}"

class QuantitativeData(DataEntry):
    content = models.DecimalField(max_digits=20, decimal_places=2)

class QualitiativeData(DataEntry):
    content = models.TextField()
