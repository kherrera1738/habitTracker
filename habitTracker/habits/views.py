from django import forms
from django.shortcuts import render
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import MainHabit, User

class CreateHabitForm(forms.Form):
    typeChoices = (
        (0, "Numeric Log"),
        (1, "Written Log")
    )
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    type = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class': 'form-check-label'}), choices=typeChoices)


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, "habits/index.html")
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
        print("creating habit")
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
def viewhabit(request, habit_id):
    habit = MainHabit.objects.get(id=habit_id)
    allData = habit.getData() 

    return render(request, "habits/viewhabit.html", {
        "habit": habit,
        "allData": allData,
    })