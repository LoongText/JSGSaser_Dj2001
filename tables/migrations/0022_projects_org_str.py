# Generated by Django 3.0.5 on 2020-11-09 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0021_auto_20201106_1309'),
    ]

    operations = [
        migrations.AddField(
            model_name='projects',
            name='org_str',
            field=models.CharField(max_length=300, null=True, verbose_name='研究机构'),
        ),
    ]
