# Generated by Django 3.0.5 on 2020-06-29 10:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='bidding',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tables.Research', verbose_name='课题招标id'),
        ),
        migrations.AlterField(
            model_name='bid',
            name='brief',
            field=models.TextField(null=True, verbose_name='申报理由及研究内容提要'),
        ),
        migrations.AlterField(
            model_name='bid',
            name='con_phone',
            field=models.CharField(max_length=20, null=True, verbose_name='课题联系人电话'),
        ),
        migrations.AlterField(
            model_name='bid',
            name='contacts',
            field=models.CharField(max_length=10, null=True, verbose_name='课题联系人'),
        ),
        migrations.AlterField(
            model_name='bid',
            name='funds',
            field=models.FloatField(null=True, verbose_name='申请经费/万元'),
        ),
        migrations.AlterField(
            model_name='bid',
            name='lea_phone',
            field=models.CharField(max_length=20, null=True, verbose_name='课题负责人电话'),
        ),
        migrations.AlterField(
            model_name='bid',
            name='leader',
            field=models.CharField(max_length=10, null=True, verbose_name='课题负责人'),
        ),
        migrations.AlterField(
            model_name='bid',
            name='re_title',
            field=models.CharField(max_length=100, null=True, verbose_name='课题名称'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='brief',
            field=models.TextField(null=True, verbose_name='机构简介'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='birth',
            field=models.DateField(null=True, verbose_name='出生日期'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='brief',
            field=models.TextField(null=True, verbose_name='简介'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='email',
            field=models.EmailField(max_length=254, null=True, verbose_name='邮箱'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='job',
            field=models.CharField(max_length=100, null=True, verbose_name='现职务职称'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='photo',
            field=models.ImageField(null=True, upload_to='participants/', verbose_name='头像'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.Organization', verbose_name='现所属单位'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='abstract',
            field=models.TextField(null=True, verbose_name='摘要'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='attached',
            field=models.FileField(null=True, upload_to='attached/%Y/%m', verbose_name='附件'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='bid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.Bid', verbose_name='对应投标'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='classify',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.Classify', verbose_name='分类'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='downloads',
            field=models.IntegerField(default=0, null=True, verbose_name='下载次数'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='key_word',
            field=models.CharField(max_length=256, null=True, verbose_name='关键词'),
        ),
        migrations.RemoveField(
            model_name='projects',
            name='lead_org',
        ),
        migrations.AddField(
            model_name='projects',
            name='lead_org',
            field=models.ManyToManyField(related_name='lead_org', to='tables.Organization', verbose_name='牵头厅局'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='reference',
            field=models.TextField(null=True, verbose_name='参考文献'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='release_date',
            field=models.DateField(null=True, verbose_name='发布时间'),
        ),
        migrations.RemoveField(
            model_name='projects',
            name='research',
        ),
        migrations.AddField(
            model_name='projects',
            name='research',
            field=models.ManyToManyField(related_name='research_org', to='tables.Organization', verbose_name='研究机构'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='text_part',
            field=models.TextField(null=True, verbose_name='正文'),
        ),
        migrations.AlterField(
            model_name='projects',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='提交用户'),
        ),
        migrations.AlterField(
            model_name='prorelations',
            name='org',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.Organization', verbose_name='机构id'),
        ),
        migrations.AlterField(
            model_name='prorelations',
            name='par',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tables.Participant', verbose_name='参与人员id'),
        ),
        migrations.AlterField(
            model_name='prorelations',
            name='pro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tables.Projects', verbose_name='成果id'),
        ),
        migrations.AlterField(
            model_name='research',
            name='brief',
            field=models.TextField(null=True, verbose_name='具体要求'),
        ),
        migrations.AlterField(
            model_name='research',
            name='classify',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.Classify', verbose_name='分类'),
        ),
        migrations.AlterField(
            model_name='research',
            name='contacts',
            field=models.CharField(max_length=10, null=True, verbose_name='联系人'),
        ),
        migrations.AlterField(
            model_name='research',
            name='end_date',
            field=models.DateField(null=True, verbose_name='结束时间'),
        ),
        migrations.AlterField(
            model_name='research',
            name='funds',
            field=models.FloatField(null=True, verbose_name='经费/万元'),
        ),
        migrations.AlterField(
            model_name='research',
            name='guidelines',
            field=models.FileField(null=True, upload_to='guide/%Y/%m', verbose_name='申报指南'),
        ),
        migrations.AlterField(
            model_name='research',
            name='phone',
            field=models.CharField(max_length=50, null=True, verbose_name='业务咨询电话'),
        ),
        migrations.AlterField(
            model_name='research',
            name='start_date',
            field=models.DateField(null=True, verbose_name='开始时间'),
        ),
        migrations.AlterField(
            model_name='research',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='组织方'),
        ),
        migrations.AlterField(
            model_name='user',
            name='id_card',
            field=models.CharField(max_length=18, null=True, verbose_name='身份证号码'),
        ),
        migrations.AlterField(
            model_name='user',
            name='org',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.Organization', verbose_name='机构关联'),
        ),
        migrations.AlterField(
            model_name='userbehavior',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户ID'),
        ),
    ]
