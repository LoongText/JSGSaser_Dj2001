# Generated by Django 3.0.5 on 2020-10-29 15:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0016_auto_20201027_1639'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='back_is_login',
        ),
        migrations.AddField(
            model_name='participant',
            name='academic_degree',
            field=models.CharField(max_length=10, null=True, verbose_name='本人学位'),
        ),
        migrations.AddField(
            model_name='participant',
            name='address',
            field=models.CharField(max_length=300, null=True, verbose_name='地址'),
        ),
        migrations.AddField(
            model_name='participant',
            name='education',
            field=models.CharField(max_length=10, null=True, verbose_name='本人最高学历'),
        ),
        migrations.AddField(
            model_name='participant',
            name='id_card',
            field=models.CharField(max_length=18, null=True, verbose_name='身份证号'),
        ),
        migrations.AddField(
            model_name='participant',
            name='postcode',
            field=models.IntegerField(null=True, verbose_name='邮编'),
        ),
        migrations.AddField(
            model_name='userregister',
            name='username',
            field=models.CharField(default='默认名', max_length=20, verbose_name='用户名'),
            preserve_default=False,
        ),
    ]