# Generated by Django 2.0.13 on 2021-06-01 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='accept_tos',
        ),
    ]
