from django.shortcuts import render
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .models import User

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
            print(1)
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

