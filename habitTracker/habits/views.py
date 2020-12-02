import json
from django import forms
from django.core.checks import messages
from django.db.models.expressions import F
from django.http.response import JsonResponse
from django.shortcuts import render
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Habit, MainHabit, User, SubHabit

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
    habit.delete()
    return HttpResponseRedirect(reverse("index")) 

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
    habit.delete()
    return HttpResponseRedirect(reverse("viewHabit", args=[mainHabitId]))

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