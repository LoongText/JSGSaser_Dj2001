# Generated by Django 3.0.5 on 2020-06-28 16:19

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id_card', models.CharField(blank=True, max_length=18, null=True, verbose_name='身份证号码')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name_plural': '用户信息表',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('bidder', models.CharField(max_length=50, verbose_name='投标方')),
                ('bidder_date', models.DateField(null=True, verbose_name='投标时间')),
                ('bidder_status', models.IntegerField(choices=[(0, '暂存'), (1, '投标中'), (2, '中标'), (3, '驳回'), (4, '删除')], default=0, verbose_name='投标状态')),
                ('conclusion_status', models.IntegerField(choices=[(0, '未开始'), (1, '审批中'), (2, '已通过'), (3, '已驳回')], default=0, verbose_name='结题状态')),
                ('funds', models.FloatField(blank=True, null=True, verbose_name='申请经费/万元')),
                ('re_title', models.CharField(blank=True, max_length=100, null=True, verbose_name='课题名称')),
                ('contacts', models.CharField(blank=True, max_length=10, null=True, verbose_name='课题联系人')),
                ('con_phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='课题联系人电话')),
                ('leader', models.CharField(blank=True, max_length=10, null=True, verbose_name='课题负责人')),
                ('lea_phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='课题负责人电话')),
                ('brief', models.TextField(blank=True, null=True, verbose_name='申报理由及研究内容提要')),
            ],
            options={
                'verbose_name_plural': '课题投标信息表',
            },
        ),
        migrations.CreateModel(
            name='Classify',
            fields=[
                ('cls_id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('cls_name', models.CharField(max_length=10, null=True, verbose_name='备注')),
            ],
        ),
        migrations.CreateModel(
            name='HotWords',
            fields=[
                ('id', models.AutoField(auto_created=True, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('hot_word', models.CharField(max_length=20, verbose_name='热词')),
                ('is_true', models.BooleanField(default=0, verbose_name='是否可用')),
                ('num', models.IntegerField(default=1, verbose_name='等级')),
                ('create_date', models.DateField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name_plural': '热词表',
                'ordering': ('-create_date',),
            },
        ),
        migrations.CreateModel(
            name='LimitNums',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('limit_word', models.FloatField(verbose_name='阈值')),
                ('is_true', models.BooleanField(default=1, verbose_name='是否可用')),
                ('level', models.IntegerField(default=1, verbose_name='等级')),
                ('create_date', models.DateField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '查重阈值表',
                'verbose_name_plural': '查重阈值表',
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=32, unique=True, verbose_name='唯一标识')),
                ('name', models.CharField(max_length=50, verbose_name='机构名称')),
                ('is_a', models.BooleanField(default=0, verbose_name='是否是甲方')),
                ('is_b', models.BooleanField(default=0, verbose_name='是否是乙方')),
                ('brief', models.TextField(blank=True, null=True, verbose_name='机构简介')),
                ('par_sum', models.IntegerField(default=0, verbose_name='研究人员总数')),
                ('pro_sum', models.IntegerField(default=0, verbose_name='成果总数')),
                ('is_show', models.BooleanField(default=1, verbose_name='是否展示')),
                ('created_date', models.DateField(auto_now_add=True, null=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name_plural': '机构信息表',
            },
        ),
        migrations.CreateModel(
            name='OrgNature',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('remarks', models.CharField(max_length=20, null=True, verbose_name='备注')),
                ('level', models.IntegerField(null=True, verbose_name='级别')),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=32, unique=True, verbose_name='唯一标识')),
                ('name', models.CharField(max_length=10, verbose_name='姓名')),
                ('gender', models.IntegerField(choices=[(1, '男'), (2, '女')], default=1, verbose_name='性别')),
                ('birth', models.DateField(blank=True, null=True, verbose_name='出生日期')),
                ('brief', models.TextField(blank=True, null=True, verbose_name='简介')),
                ('job', models.CharField(blank=True, max_length=100, null=True, verbose_name='现职务职称')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='邮箱')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='participants/', verbose_name='头像')),
                ('created_date', models.DateField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('pro_sum', models.IntegerField(default=0, verbose_name='成果总数')),
                ('is_show', models.BooleanField(default=1, verbose_name='是否展示')),
                ('name_pinyin', models.CharField(max_length=100, null=True, verbose_name='姓名的全拼')),
                ('unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.Organization', verbose_name='现所属单位')),
            ],
            options={
                'verbose_name_plural': '研究人员信息表',
            },
        ),
        migrations.CreateModel(
            name='Projects',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=32, unique=True, verbose_name='唯一标识')),
                ('name', models.CharField(max_length=200, verbose_name='题名')),
                ('lead_org', models.CharField(blank=True, max_length=100, null=True, verbose_name='牵头厅局')),
                ('research', models.CharField(blank=True, max_length=100, null=True, verbose_name='研究机构')),
                ('key_word', models.CharField(blank=True, max_length=256, null=True, verbose_name='关键词')),
                ('abstract', models.TextField(blank=True, null=True, verbose_name='摘要')),
                ('attached', models.FileField(blank=True, null=True, upload_to='attached/%Y/%m', verbose_name='附件')),
                ('reference', models.TextField(blank=True, null=True, verbose_name='参考文献')),
                ('downloads', models.IntegerField(blank=True, default=0, null=True, verbose_name='下载次数')),
                ('views', models.IntegerField(default=0, verbose_name='浏览次数')),
                ('export', models.IntegerField(default=0, verbose_name='导出次数')),
                ('text_part', models.TextField(blank=True, null=True, verbose_name='正文')),
                ('release_date', models.DateField(blank=True, null=True, verbose_name='发布时间')),
                ('update_date', models.DateField(auto_now=True, verbose_name='最新修改时间')),
                ('status', models.IntegerField(choices=[(0, '不显示'), (1, '合格'), (2, '待完善'), (3, '审批中'), (4, '不合格'), (5, '删除')], default=1, verbose_name='状态')),
                ('bid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.Bid', verbose_name='对应投标')),
                ('classify', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pro_cls', to='tables.Classify', verbose_name='分类')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pro_user', to=settings.AUTH_USER_MODEL, verbose_name='提交用户')),
            ],
            options={
                'verbose_name_plural': '成果信息表',
            },
        ),
        migrations.CreateModel(
            name='SensitiveWords',
            fields=[
                ('id', models.AutoField(auto_created=True, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('sen_word', models.CharField(max_length=20, verbose_name='敏感词')),
                ('is_true', models.BooleanField(default=1, verbose_name='是否可用')),
                ('level', models.IntegerField(default=1, verbose_name='等级')),
                ('create_date', models.DateField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name_plural': '敏感词表',
                'ordering': ('-create_date',),
            },
        ),
        migrations.CreateModel(
            name='UserDownloadBehavior',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('pro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tables.Projects', verbose_name='成果对应id')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户ID')),
            ],
            options={
                'verbose_name_plural': '用户下载行为数据表',
            },
        ),
        migrations.CreateModel(
            name='UserClickBehavior',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('pro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tables.Projects', verbose_name='成果对应id')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户ID')),
            ],
            options={
                'verbose_name_plural': '用户浏览行为数据表',
            },
        ),
        migrations.CreateModel(
            name='UserBehavior',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=100, verbose_name='用户行为关键词')),
                ('search_con', models.TextField(verbose_name='行为条件')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='搜索时间')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ub_user', to=settings.AUTH_USER_MODEL, verbose_name='用户ID')),
            ],
            options={
                'verbose_name_plural': '用户行为数据表',
            },
        ),
        migrations.CreateModel(
            name='Research',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=32, unique=True, verbose_name='唯一标识')),
                ('name', models.CharField(max_length=100, verbose_name='题目')),
                ('funds', models.FloatField(blank=True, null=True, verbose_name='经费/万元')),
                ('brief', models.TextField(blank=True, null=True, verbose_name='具体要求')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='开始时间')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='结束时间')),
                ('status', models.IntegerField(choices=[(0, '未开启'), (1, '招标中'), (2, '推进中'), (3, '已结题'), (4, '删除')], default=0, verbose_name='状态')),
                ('contacts', models.CharField(blank=True, max_length=10, null=True, verbose_name='联系人')),
                ('phone', models.CharField(blank=True, max_length=50, null=True, verbose_name='业务咨询电话')),
                ('guidelines', models.FileField(blank=True, null=True, upload_to='guide/%Y/%m', verbose_name='申报指南')),
                ('created_date', models.DateField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('classify', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='re_cls', to='tables.Classify', verbose_name='分类')),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='re_user', to=settings.AUTH_USER_MODEL, verbose_name='组织方')),
            ],
            options={
                'verbose_name_plural': '课题招标信息表',
                'ordering': ('-start_date',),
            },
        ),
        migrations.CreateModel(
            name='ProRelations',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('roles', models.IntegerField(choices=[(1, '组长'), (2, '副组长'), (3, '组员')], null=True, verbose_name='课题组内角色')),
                ('score', models.FloatField(default=1, verbose_name='评价指数')),
                ('speciality', models.CharField(max_length=50, null=True, verbose_name='业务专长')),
                ('job', models.CharField(max_length=50, null=True, verbose_name='职务职称')),
                ('task', models.CharField(max_length=200, null=True, verbose_name='课题组内承担的任务')),
                ('is_eft', models.BooleanField(default=0, verbose_name='是否有效')),
                ('org', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pro_org', to='tables.Organization', verbose_name='机构id')),
                ('par', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pro_par', to='tables.Participant', verbose_name='参与人员id')),
                ('pro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pro', to='tables.Projects', verbose_name='成果id')),
            ],
        ),
        migrations.AddField(
            model_name='organization',
            name='nature',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.OrgNature', verbose_name='机构性质'),
        ),
        migrations.AddField(
            model_name='bid',
            name='bidding',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='res', to='tables.Research', verbose_name='课题招标id'),
        ),
        migrations.AddField(
            model_name='bid',
            name='submitter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='提交者'),
        ),
        migrations.AddField(
            model_name='user',
            name='org',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tables.Organization', verbose_name='机构关联'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
