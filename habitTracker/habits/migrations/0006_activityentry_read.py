# Generated by Django 3.1.1 on 2020-11-12 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0005_remove_activityentry_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityentry',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
