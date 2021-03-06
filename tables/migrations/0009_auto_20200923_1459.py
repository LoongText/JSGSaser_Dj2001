# Generated by Django 3.0.5 on 2020-09-23 14:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0008_orgnature_ord_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectsMark',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('remarks', models.CharField(max_length=20, null=True, verbose_name='备注')),
                ('level', models.IntegerField(null=True, verbose_name='级别')),
            ],
        ),
        migrations.AddField(
            model_name='projects',
            name='good_mark',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.ProjectsMark', verbose_name='优秀成果标志'),
        ),
    ]
