# Generated by Django 3.1.1 on 2020-12-03 01:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0013_auto_20201118_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habit',
            name='viewers',
            field=models.ManyToManyField(blank=True, default=None, related_name='viewing', to=settings.AUTH_USER_MODEL),
        ),
    ]