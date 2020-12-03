from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.loginView, name="login"),
    path("register", views.registerView, name="register"),
    path("logout", views.logoutView, name="logout"),
    path("createHabit", views.createHabit, name="createHabit"),
    path("habit/<int:habit_id>", views.viewHabit, name="viewHabit"),
    path("habit/<int:habit_id>/add", views.addHabitData, name="addHabitData"),
    path("habit/<int:habit_id>/edit", views.editHabit, name="editHabit"),
    path("habit/<int:habit_id>/delete", views.deleteHabit, name="deleteHabit"),
    path("habit/<int:mainhabit_id>/createSubHabit", views.createSubHabit, name="createSubHabit"),
    path("subhabit/<int:subhabit_id>", views.viewSubHabit, name="viewSubHabit"),
    path("subhabit/<int:subhabit_id>/add", views.addSubHabitData, name="addSubHabitData"),
    path("subhabit/<int:subhabit_id>/delete", views.deleteSubHabit, name="deleteSubHabit"),
    path("subhabit/<int:subhabit_id>/edit", views.editSubHabit, name="editSubHabit"),
    path("habit/<int:habit_id>/<int:entry_id>/edit", views.editEntry, name="editEntry"),
    path("habit/<int:habit_id>/<int:entry_id>/delete", views.deleteEntry, name="deleteEntry"),
    path("sendRequest", views.sendRequest, name="sendRequest"),
    path("getRequestsCount", views.getRequestCount, name="getRequestCount"),
    path("getViewRequests", views.getViewRequests, name="getViewRequests"),
    path("replyRequest", views.replyRequest, name="replyRequest"),
    path("viewOthersHabit/<int:habit_id>", views.viewOthersHabit, name="viewOthersHabit")
]