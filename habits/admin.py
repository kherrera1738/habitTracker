from django.contrib import admin
from .models import User, Habit, MainHabit, SubHabit, ActivityLog, ActivityEntry, ViewRequest, DataSet, QualitativeData, QuantitativeData, QualitativeDataSet, QuantitativeDataSet

# Register your models here.
admin.site.register(User)
admin.site.register(Habit)
admin.site.register(MainHabit)
admin.site.register(SubHabit)
admin.site.register(ActivityLog)
admin.site.register(ActivityEntry)
admin.site.register(ViewRequest)
admin.site.register(DataSet)
admin.site.register(QualitativeData)
admin.site.register(QuantitativeData)
admin.site.register(QualitativeDataSet)
admin.site.register(QuantitativeDataSet)
