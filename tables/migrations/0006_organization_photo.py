# Generated by Django 3.0.5 on 2020-08-05 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0005_runinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='photo',
            field=models.ImageField(null=True, upload_to='organizations/', verbose_name='头像'),
        ),
    ]
