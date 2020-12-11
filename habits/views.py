import json
import pytz
from datetime import datetime, timedelta, date

from django import forms
from django.core.checks import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.expressions import F
from django.db import IntegrityError
from django.http.response import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Habit, MainHabit, User, SubHabit, ViewRequest

class CreateHabitForm(forms.Form):
    typeChoices = (
        (0, "Numeric Log"),
        (1, "Written Log")
    )
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    type = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'form-check-label'}), choices=typeChoices)

class AddHabitDataForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}))

class EditEntryForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}))

class CreateSubHabitForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

class EditHabitForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, "habits/index.html", {
        'habitSet': MainHabit.objects.filter(owner=request.user) 
    })
    return HttpResponseRedirect(reverse("login"))

def loginView(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "habits/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "habits/login.html")

def registerView(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "habits/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "habits/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "habits/register.html")

def logoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def about(request):
    return render(request, "habits/about.html")

@login_required
def createHabit(request):   
    if request.method == "POST":
        form = CreateHabitForm(request.POST)
        if form.is_valid():
            habitName = form.cleaned_data["name"]
            dataType = int(form.cleaned_data["type"])
            if habitName and dataType >= 0 and dataType <= 1:
                try:
                    mainhabit = MainHabit.objects.create(name=habitName, owner=request.user, dataType=dataType)
                    mainhabit.save()
                    return HttpResponseRedirect(reverse("index"))
                except IntegrityError:
                    return render(request, "habits/createHabit.html", {
                        "message": "Habit name already taken."
                    })
            else:
                return render(request, "habits/createHabit.html", {
                    "message": "Missing input."
                })
        else:
            return render(request, "habits/createHabit.html", {
                "message": "Invalid form."
            })
    else:
        return render(request, "habits/createHabit.html", {
            "form": CreateHabitForm() 
        })

@login_required
def viewHabit(request, habit_id):
    habit = MainHabit.objects.get(id=habit_id)
    allData = habit.getData().order_by('-date') 

    return render(request, "habits/viewHabit.html", {
        "habit": habit,
        "allData": allData
    })

@login_required
def addHabitData(request, habit_id):
    habit = MainHabit.objects.get(id=habit_id)
    contextHash = {
        'habit': habit,
        'form': AddHabitDataForm()
    }

    if request.method == "POST":
        form = AddHabitDataForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['content']
            if habit.addData(data):
                return HttpResponseRedirect(reverse("viewHabit", args=[habit.id]))
            else:
                contextHash['message'] = "Unable to add data. Did you enter the right type?"
        else:
            contextHash['message'] = "Something went wrong when adding data. Try again later"

    return render(request, "habits/addHabitData.html", contextHash)

@login_required
def deleteHabit(request, habit_id):
    habit = MainHabit.objects.get(id=habit_id)
    if request.method == "POST":
        if "yes" in request.POST:
            habit.delete()
            return HttpResponseRedirect(reverse("index"), {
                'message': "Habit Succesfully deleted"
            })
        else:
            return HttpResponseRedirect(reverse("index"))
    return render(request, "habits/deleteHabit.html", {
        "habit": habit
    })

@login_required
def editHabit(request, habit_id):
    mainhabit = MainHabit.objects.get(id=habit_id)
    contextHash = {
        "form": EditHabitForm(),
        "habit": mainhabit
    }
    if request.method == "POST":
        form = EditHabitForm(request.POST)
        if form.is_valid():
            habitName = form.cleaned_data["name"]
            if habitName:
                try:
                    mainhabit.name = habitName
                    mainhabit.save()
                    return HttpResponseRedirect(reverse("viewHabit", args=[mainhabit.id]))
                except IntegrityError:
                    contextHash["message"] = "Habit name already taken"
            else:
                contextHash["message"] = "Missing input"
        else:
            contextHash["message"] = "Invalid form"
    return render(request, "habits/editHabit.html", contextHash)

@login_required
def createSubHabit(request, mainhabit_id):
    mainhabit = MainHabit.objects.get(id=mainhabit_id)
    contextHash = {
        "mainhabit": mainhabit,
        "form": CreateSubHabitForm()
    }
    if request.method == "POST":
        form = CreateSubHabitForm(request.POST)
        if form.is_valid():
            habitName = form.cleaned_data["name"]
            if habitName:
                try:
                    mainhabit.createSubhabit(habitName)
                    return HttpResponseRedirect(reverse("viewHabit", args=[mainhabit_id]))
                except IntegrityError:
                    contextHash["message"] = "Habit name already taken"
            else:
                contextHash["message"] = "Missing input"
        else:
            contextHash["message"] = "Invalid form"
    return render(request, "habits/createSubHabit.html", contextHash)

@login_required
def viewSubHabit(request, subhabit_id):
    habit = SubHabit.objects.get(id=subhabit_id)
    allData = habit.getData().order_by('-date') 

    return render(request, "habits/viewSubHabit.html", {
        "habit": habit,
        "allData": allData
    })

@login_required
def addSubHabitData(request, subhabit_id):
    habit = SubHabit.objects.get(id=subhabit_id)
    contextHash = {
        'habit': habit,
        'form': AddHabitDataForm()
    }

    if request.method == "POST":
        form = AddHabitDataForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['content']
            if habit.addData(data):
                return HttpResponseRedirect(reverse("viewSubHabit", args=[habit.id]))
            else:
                contextHash['message'] = "Unable to add data. Did you enter the right type?"
        else:
            contextHash['message'] = "Something went wrong when adding data. Try again later"

    return render(request, "habits/addSubHabitData.html", contextHash)

@login_required
def deleteSubHabit(request, subhabit_id):
    habit = SubHabit.objects.get(id=subhabit_id)
    mainHabitId = habit.mainHabit_id
    if request.method == "POST":
        if "yes" in request.POST:
            habit.delete()
            return HttpResponseRedirect(reverse("viewHabit", args=[mainHabitId]), {
                'message': "Habit Succesfully deleted"
            })
        else:
            return HttpResponseRedirect(reverse("viewHabit", args=[mainHabitId]))
    return render(request, "habits/deleteSubHabit.html", {
        "habit": habit
    })

@login_required
def editSubHabit(request, subhabit_id):
    subhabit = SubHabit.objects.get(id=subhabit_id)
    contextHash = {
        "form": EditHabitForm(),
        "habit": subhabit
    }
    if request.method == "POST":
        form = EditHabitForm(request.POST)
        if form.is_valid():
            habitName = form.cleaned_data["name"]
            if habitName:
                try:
                    subhabit.name = habitName
                    subhabit.save()
                    return HttpResponseRedirect(reverse("viewSubHabit", args=[subhabit.id]))
                except IntegrityError:
                    contextHash["message"] = "Habit name already taken"
            else:
                contextHash["message"] = "Missing input"
        else:
            contextHash["message"] = "Invalid form"
    return render(request, "habits/editSubHabit.html", contextHash)

@login_required
def editEntry(request, habit_id, entry_id):
    if MainHabit.objects.filter(id=habit_id).exists():
        habit = MainHabit.objects.get(id=habit_id)
    else:
        habit = SubHabit.objects.get(id=habit_id)
    entry = habit.getData().get(id=entry_id)
    contextHash = {
        "habit": habit,
        "entry": entry,
        "form": EditEntryForm()
    }

    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['content']
            if habit.updateEntry(entry_id, data):
                if(isinstance(habit, MainHabit)):
                    return HttpResponseRedirect(reverse("viewHabit", args=[habit.id]))
                else:
                    return HttpResponseRedirect(reverse("viewSubHabit", args=[habit.id]))
            else:
                contextHash['message'] = "Unable to add data. Did you enter the right type?"
        else:
            contextHash['message'] = "Something went wrong when adding data. Try again later"

    return render(request, "habits/editEntry.html", contextHash)

@login_required
def deleteEntry(request, habit_id, entry_id):
    if MainHabit.objects.filter(id=habit_id).exists():
        habit = MainHabit.objects.get(id=habit_id)
    else:
        habit = SubHabit.objects.get(id=habit_id)
    entry = habit.getData().get(id=entry_id)
    entry.delete()
    if(isinstance(habit, MainHabit)):
        return HttpResponseRedirect(reverse("viewHabit", args=[habit.id]))
    else:
        return HttpResponseRedirect(reverse("viewSubHabit", args=[habit.id]))
        
@csrf_exempt
@login_required
def sendRequest(request):

    attrs = {"to", "habit"}

    reply = {
        "success" : True,
        "message" : "Request Sent!"
    }
    data = json.loads(request.body)
    if request.method == "POST" and data.keys() >= attrs:
        try:
            habitId = int(data.get("habit"))
        except SyntaxError:
            reply["success"] = False
            reply["message"] = "Seems like soemthing went wrong. Try again later"
            return JsonResponse(reply)
    
        if User.objects.filter(username=data.get("to")).exists() and \
            Habit.objects.filter(id=habitId).exists():

            if(SubHabit.objects.filter(id=habitId).exists()):
                sb = SubHabit.objects.get(id=habitId)
                
                if(ViewRequest.objects.filter(associatedHabit=sb.mainHabit).exists()):
                    reply["success"] = False
                    reply["message"] = "MainHabit already has sent request"  
                    return JsonResponse(reply)                                  

            to = User.objects.get(username=data.get("to"))
            habit = Habit.objects.get(id=habitId)
            if not habit.sendRequest(to.id):
                reply["success"] = False
                reply["message"] = "Request already exists"
        else:
            reply["success"] = False
            reply["message"] = "Seems like soemthing went wrong. Please make sure the username is correct"

    return JsonResponse(reply)

@csrf_exempt
@login_required
def getRequestCount(request):
    reply = {
        "count" : request.user.recievedRequests.count()
    }

    return JsonResponse(reply)

@csrf_exempt
@login_required
def getViewRequests(request):
    viewRequests = request.user.recievedRequests.order_by("-id").all()
    return JsonResponse([viewRequest.serialize() for viewRequest in viewRequests], safe=False)

@csrf_exempt
@login_required
def replyRequest(request):
    reply = {}
    if request.method == "POST":
        data = json.loads(request.body)
        dataNeeded = {"requestId", "reply"}
        if data.keys() >= dataNeeded and ViewRequest.objects.filter(id=data.get("requestId")).exists():
            viewRequest = ViewRequest.objects.get(id=data.get("requestId"))
            if data.get("reply") == "Accept":
                reply["success"] = True
                reply["message"] = "Request was accepted"
                viewRequest.accept()
            elif data.get("reply") == "Reject":
                viewRequest.reject()
                reply["success"] = True
                reply["message"] = "Request was rejected"
            else:
                reply["success"] = False
                reply["message"] = "Could not accept or reject request"
            return JsonResponse(reply)
    reply["success"] = False
    reply["message"] = "Request may not exist"
    return JsonResponse(reply)

@login_required
def viewOthersHabit(request, habit_id):
    if MainHabit.objects.filter(id=habit_id).exists():
        return HttpResponseRedirect(reverse("viewHabit", args=[habit_id]))
    else:
        return HttpResponseRedirect(reverse("viewSubHabit", args=[habit_id]))

@csrf_exempt
@login_required
def getHabitData(request):
    reply = {
        "success": False
    }

    data = json.loads(request.body)
    if MainHabit.objects.filter(id=data["id"]).exists():
        habit = MainHabit.objects.get(id=data["id"])
    else:
        habit = SubHabit.objects.get(id=data["id"])

    if data["getBy"] == "thisWeek":
        today = timezone.now().date()
        sunday = today - timedelta(days=(today.isocalendar()[2]))
        saturday = sunday + timedelta(days=6)

        sunday = datetime.combine(sunday, datetime.min.time(), tzinfo=pytz.utc)
        saturday = datetime.combine(saturday, datetime.max.time(), tzinfo=pytz.utc)
        reply["success"] = True
        reply["data"] = [datapoint.serialize() for datapoint in habit.getByDateRange(sunday, saturday).order_by('-id').all()]
    else:
        # start = datetime.combine(date.fromisoformat(data["start"]), datetime.min.time(), tzinfo=pytz.utc)
        start = datetime.strptime(data['start'], '%Y-%m-%d')
        start = start.replace(tzinfo=pytz.utc)

        end = None
        if data["range"] == "range":
            end = datetime.strptime(data['end'], '%Y-%m-%d')
            end = end.replace(tzinfo=pytz.utc)
        
        if data["getBy"] == "day":
            if data["range"] == "range":
                reply["data"] = [datapoint.serialize() for datapoint in habit.getByDateRange(start, end).order_by('-id').all()]
            else:
                reply["data"] = reply["data"] = [datapoint.serialize() for datapoint in habit.getByDate(start).order_by('-id').all()]
        elif data["getBy"] == "month":
            if data["range"] == "range":
                reply["data"] = [datapoint.serialize() for datapoint in habit.getByMonthAndYearRange(start, end).order_by('-id').all()]
            else:
                reply["data"] = reply["data"] = [datapoint.serialize() for datapoint in habit.getByMonthAndYear(start).order_by('-id').all()]
        else:
            if data["range"] == "range":
                reply["data"] = [datapoint.serialize() for datapoint in habit.getByYearRange(start, end).order_by('-id').all()]
            else:
                reply["data"] = reply["data"] = [datapoint.serialize() for datapoint in habit.getByYear(start).order_by('-id').all()]
        reply["success"] = True

    return JsonResponse(reply, safe=False)