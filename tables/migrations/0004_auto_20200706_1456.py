# Generated by Django 3.0.5 on 2020-07-06 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0003_auto_20200702_1935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projects',
            name='update_date',
            field=models.DateField(auto_now_add=True, verbose_name='上传时间'),
        ),
    ]
