# Generated by Django 3.0.5 on 2020-11-16 10:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0025_auto_20201112_1049'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='competent_dpt',
        ),
    ]