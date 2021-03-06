# Generated by Django 3.0.5 on 2020-10-20 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0012_auto_20201016_1711'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projects',
            name='release_time',
        ),
        migrations.AddField(
            model_name='projects',
            name='approval_time',
            field=models.DateField(null=True, verbose_name='审批时间'),
        ),
        migrations.AlterField(
            model_name='userregister',
            name='unit_nature',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.OrgNature', verbose_name='单位属性'),
        ),
    ]
