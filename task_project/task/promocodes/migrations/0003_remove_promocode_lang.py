# Generated by Django 2.0.13 on 2021-06-01 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promocodes', '0002_promocodeusage_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promocode',
            name='lang',
        ),
    ]
