from django.contrib import admin
from .models import User, MainHabit, SubHabit, ActivityLog, ActivityEntry, ViewRequest, DataSet, QualitiativeData, QuantitativeData

# Register your models here.
admin.site.register(User)
admin.site.register(MainHabit)
admin.site.register(SubHabit)
admin.site.register(ActivityLog)
admin.site.register(ActivityEntry)
admin.site.register(ViewRequest)
admin.site.register(DataSet)
admin.site.register(QualitiativeData)
admin.site.register(QuantitativeData)
