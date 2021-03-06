from django.db import models
import random
import string
from django.conf import settings
from pypinyin import lazy_pinyin
from django.contrib.auth.models import AbstractUser


class Classify(models.Model):
    """
    课题分类表
    """
    cls_id = models.AutoField(primary_key=True, verbose_name='ID')
    cls_name = models.CharField(max_length=10, verbose_name='备注', null=True)

    def __str__(self):
        return self.cls_name


class Research(models.Model):
    """
    申请课题信息表(招标信息表)
    """
    STATUS_CHOICE = ((0, '未开启'), (1, '招标中'), (2, '推进中'), (3, '已结题'), (4, '删除'))
    id = models.AutoField(primary_key=True, verbose_name='ID')
    uuid = models.CharField(max_length=32, verbose_name='唯一标识', null=False, unique=True)
    name = models.CharField(max_length=100, null=False, verbose_name='题目')
    classify = models.ForeignKey(Classify, on_delete=models.CASCADE, null=True, verbose_name='分类')
    funds = models.FloatField(verbose_name='经费/万元', null=True)
    brief = models.TextField(verbose_name='具体要求', null=True)
    start_date = models.DateField(verbose_name='开始时间', null=True)
    end_date = models.DateField(verbose_name='结束时间', null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, verbose_name='状态', default=0)
    contacts = models.CharField(max_length=10, verbose_name='联系人', null=True)
    phone = models.CharField(max_length=50, verbose_name='业务咨询电话', null=True)
    guidelines = models.FileField(verbose_name='申报指南', null=True, upload_to='guide/%Y/%m')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="组织方", null=False)
    created_date = models.DateField(auto_now_add=True, verbose_name='创建时间', null=True)
    con_date = models.DateField(verbose_name='结题时间', null=True)

    class Meta:
        verbose_name_plural = '课题招标信息表'
        ordering = ('-start_date',)

    def save(self, *args, **kwargs):
        # 自动填写uuid
        if not self.uuid:
            self.uuid = ''.join(random.sample(string.ascii_letters + string.digits, 32))
        # if not self.user:
        #     self.user = self.user
        # 调用父类的save 方法将数据保存到数据库中
        super(Research, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Bid(models.Model):
    """
    投标信息表
    """
    BIDDER_STATUS_CHOICE = ((0, '暂存'), (1, '投标中'), (2, '初审通过'), (3, '初审驳回'), (4, '删除'),
                            (5, '立项中标'), (6, '立项驳回'))
    INTERIM_REVIEW_STATUS_CHOICE = ((0, '未开始'), (1, '审批中'), (2, '已通过'), (3, '已驳回'), (4, '待提交'))
    CONCLUSION_STATUS_CHOICE = ((0, '未开始'), (1, '审批中'), (2, '已通过'), (3, '已驳回'), (4, '待提交'))
    id = models.AutoField(primary_key=True, verbose_name='ID')
    bidder = models.CharField(max_length=50, verbose_name='投标方', null=False)
    bidding = models.ForeignKey(Research, on_delete=models.CASCADE, verbose_name='课题招标id')
    bidder_date = models.DateField(verbose_name='投标时间', null=True)
    bidder_status = models.IntegerField(choices=BIDDER_STATUS_CHOICE, verbose_name='投标状态', default=0)
    interim_status = models.IntegerField(choices=INTERIM_REVIEW_STATUS_CHOICE, verbose_name='中期评审状态', default=0)
    conclusion_status = models.IntegerField(choices=CONCLUSION_STATUS_CHOICE, verbose_name='结题状态', default=0)
    bid_trial_date = models.DateTimeField(verbose_name='初审时间', null=True)
    bid_trial_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='初审用户',
                                       related_name='bid_trial_user', null=True)
    bid_lix_date = models.DateTimeField(verbose_name='立项时间', null=True)
    bid_interim_date = models.DateTimeField(verbose_name='中期评审时间', null=True)
    bid_con_date = models.DateTimeField(verbose_name='结题时间', null=True)
    funds = models.FloatField(verbose_name='申请经费/万元', null=True)
    re_title = models.CharField(max_length=100, verbose_name='课题名称', null=True)
    contacts = models.CharField(max_length=10, verbose_name='课题联系人', null=True)
    con_phone = models.CharField(max_length=20, verbose_name='课题联系人电话', null=True)
    leader = models.CharField(max_length=10, verbose_name='课题负责人', null=True)
    lea_phone = models.CharField(max_length=20, verbose_name='课题负责人电话', null=True)
    brief = models.TextField(verbose_name='申报理由及研究内容提要', null=True)
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='提交者')
    bid_attached = models.FileField(verbose_name='附件', null=True, upload_to='bid/%Y/%m')
    interim_attached = models.FileField(verbose_name='中期报告', null=True, upload_to='bid/%Y/%m')
    conclusion_attached = models.FileField(verbose_name='结题报告', null=True, upload_to='bid/%Y/%m')

    class Meta:
        verbose_name_plural = '课题投标信息表'
        # ordering = ('-bidder_date',)


class OrgNature(models.Model):
    """
    机构性质表
    """
    id = models.AutoField(primary_key=True, verbose_name='ID')
    remarks = models.CharField(max_length=20, verbose_name='备注', null=True)
    level = models.IntegerField(verbose_name='级别', null=True)
    ord_by = models.IntegerField(verbose_name='排序', null=False, default=1)

    def __str__(self):
        return self.remarks


class Organization(models.Model):
    """
    机构信息表
    """
    id = models.AutoField(primary_key=True, verbose_name='ID')
    uuid = models.CharField(max_length=32, verbose_name='唯一标识', null=False, unique=True)
    id_card_code = models.CharField(max_length=18, verbose_name="社会信用码", null=True)
    name = models.CharField(max_length=100, null=False, verbose_name='机构名称')
    superior_unit = models.IntegerField(verbose_name='上级单位', default=0)
    nature = models.ForeignKey(OrgNature, verbose_name='机构性质', null=True, on_delete=models.CASCADE)
    brief = models.TextField(verbose_name='机构简介', null=True)
    par_sum = models.IntegerField(verbose_name='研究人员总数', default=0)
    pro_sum = models.IntegerField(verbose_name='成果总数', default=0)
    is_show = models.BooleanField(verbose_name='是否展示', default=1)
    created_date = models.DateField(auto_now_add=True, verbose_name='创建时间', null=True, editable=False)
    register_type = models.CharField(max_length=100, verbose_name="注册类型", null=True)
    register_capital = models.FloatField(verbose_name="注册资本", null=True)
    register_date = models.DateField(verbose_name="注册时间", null=True)
    address = models.TextField(verbose_name="地址", null=True)
    postcode = models.IntegerField(verbose_name="邮政编码", null=True)
    unit_tel = models.CharField(max_length=20, verbose_name="单位电话", null=True)
    unit_fax = models.CharField(max_length=20, verbose_name="单位传真", null=True)
    photo = models.ImageField(upload_to='organizations/logo/%Y/%m', verbose_name='单位logo', null=True)
    certification_materials = models.FileField(verbose_name="证明材料", null=True,
                                               upload_to='organizations/materials/%Y/%m')
    business_license = models.FileField(verbose_name="营业执照", null=True, upload_to='organizations/license/%Y/%m')

    class Meta:
        verbose_name_plural = '机构信息表'

    def save(self, *args, **kwargs):
        # 自动填写uuid
        if not self.uuid:
            self.uuid = ''.join(random.sample(string.ascii_letters + string.digits, 32))
        # 调用父类的save 方法将数据保存到数据库中
        super(Organization, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def par_sum_add(self):
        # 研究人员总数+1
        self.par_sum += 1
        self.save(update_fields=['par_sum'])

    def pro_sum_add(self):
        # 成果总数+1
        self.pro_sum += 1
        self.save(update_fields=['pro_sum'])

    def pro_sum_cut(self):
        # 成果总数-1
        if self.pro_sum > 0:
            self.pro_sum -= 1
        else:
            self.pro_sum = 0
        self.save(update_fields=['pro_sum'])

    def par_sum_cut(self):
        # 研究人员总数-1
        if self.par_sum > 0:
            self.par_sum -= 1
        else:
            self.par_sum = 0
        self.save(update_fields=['par_sum'])


class ProjectsMark(models.Model):
    """
    优秀成果标志表
    """
    id = models.AutoField(primary_key=True, verbose_name='ID')
    remarks = models.CharField(max_length=20, verbose_name='备注', null=True)
    level = models.IntegerField(verbose_name='级别', null=True)

    def __str__(self):
        return self.remarks


class Projects(models.Model):
    """
    课题成果表
    """
    STATUS_CHOICE = ((0, '不显示'), (1, '合格'), (2, '待完善'), (3, '审批中'), (4, '不合格'), (5, '删除'))
    id = models.AutoField(primary_key=True, verbose_name='ID')
    uuid = models.CharField(max_length=50, verbose_name='唯一标识', null=False, unique=True)
    name = models.CharField(max_length=200, null=False, verbose_name='题名')
    lead_org = models.ManyToManyField(Organization, verbose_name='牵头厅局', related_name='lead_org')
    research = models.ManyToManyField(Organization, verbose_name='研究机构', related_name='research_org')
    classify = models.ForeignKey(Classify, on_delete=models.CASCADE, null=True, verbose_name='分类')
    key_word = models.CharField(max_length=256, null=True, verbose_name='关键词')
    abstract = models.TextField(null=True, verbose_name='摘要')
    attached = models.FileField(verbose_name='附件', null=True, upload_to='attached/%Y/%m')
    reference = models.TextField(null=True, verbose_name='参考文献')
    downloads = models.IntegerField(null=True, verbose_name='下载次数', default=0)
    views = models.IntegerField(verbose_name='浏览次数', default=0)
    export = models.IntegerField(verbose_name='导出次数', default=0)
    text_part = models.TextField(null=True, verbose_name='正文')
    release_date = models.DateField(null=True, verbose_name='发布时间')
    update_date = models.DateField(auto_now_add=True, verbose_name='上传时间')
    approval_time = models.DateField(verbose_name='审批时间', null=True)
    status = models.IntegerField(choices=STATUS_CHOICE, default=1, verbose_name='状态')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="提交用户", null=True)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, verbose_name="对应投标", null=True)
    good_mark = models.ForeignKey(ProjectsMark, on_delete=models.CASCADE, verbose_name="优秀成果标志", null=True)
    pro_source = models.CharField(max_length=10, verbose_name='来源', default='iser')  # iser,cnki
    org_str = models.CharField(max_length=300, verbose_name='研究机构', null=True)  # 来源是cnki数据的研究机构字符串

    class Meta:
        verbose_name_plural = '成果信息表'

    def save(self, *args, **kwargs):
        # 自动填写uuid
        if not self.uuid:
            self.uuid = ''.join(random.sample(string.ascii_letters + string.digits, 32))
        # 调用父类的save 方法将数据保存到数据库中
        super(Projects, self).save(*args, **kwargs)

    def views_num_update(self):
        # 点击量+1
        self.views += 1
        self.save(update_fields=['views'])

    def download_num_update(self):
        # 下载量+1
        self.downloads += 1
        self.save(update_fields=['downloads'])

    def export_num_update(self):
        # 导出量+1
        self.export += 1
        self.save(update_fields=['export'])


class Participant(models.Model):
    """
    参与人员信息表
    """
    GENDER_CHOICES = ((1, '男'), (2, '女'))
    id = models.AutoField(primary_key=True, verbose_name='ID')
    uuid = models.CharField(max_length=32, verbose_name='唯一标识', null=False, unique=True)
    id_card = models.CharField(max_length=18, verbose_name="身份证号", null=True)
    name = models.CharField(max_length=30, null=False, verbose_name='姓名')
    cell_phone = models.CharField(max_length=18, null=True, verbose_name="手机号")
    gender = models.IntegerField(choices=GENDER_CHOICES, verbose_name='性别', default=1)
    birth = models.DateField(null=True, verbose_name='出生日期')
    education = models.CharField(max_length=100, null=True, verbose_name="本人最高学历")
    academic_degree = models.CharField(max_length=100, null=True, verbose_name="本人学位")
    address = models.TextField(null=True, verbose_name="地址")
    postcode = models.IntegerField(null=True, verbose_name="邮编")
    unit = models.ForeignKey(Organization, null=True, verbose_name='现所属单位',
                             on_delete=models.CASCADE, related_name='pts')
    brief = models.TextField(null=True, verbose_name='简介')
    job = models.CharField(max_length=100, verbose_name='现职务职称', null=True)
    research_direction = models.CharField(max_length=100, verbose_name='研究方向', null=True)
    email = models.EmailField(verbose_name='邮箱', null=True)
    photo = models.ImageField(upload_to='participants/portrait/%Y/%m', verbose_name='头像', null=True)
    id_card_photo_positive = models.ImageField(upload_to='participants/id_card/%Y/%m', verbose_name='身份证正面', null=True)
    id_card_photo_reverse = models.ImageField(upload_to='participants/id_card/%Y/%m', verbose_name='身份证反面', null=True)
    created_date = models.DateField(auto_now_add=True, verbose_name='创建时间', null=True)
    pro_sum = models.IntegerField(verbose_name='成果总数', default=0)
    is_show = models.BooleanField(verbose_name='是否展示', default=1)
    name_pinyin = models.CharField(max_length=100, verbose_name='姓名的全拼', null=True)
    level = models.IntegerField(verbose_name="vip级别", default=1)

    class Meta:
        verbose_name_plural = '研究人员信息表'

    def save(self, *args, **kwargs):
        # 自动填写uuid
        if not self.uuid:
            self.uuid = ''.join(random.sample(string.ascii_letters + string.digits, 32))
        if not self.name_pinyin:
            self.name_pinyin = ''.join(lazy_pinyin(self.name))
        # 调用父类的save 方法将数据保存到数据库中
        super(Participant, self).save(*args, **kwargs)

    def pro_sum_add(self):
        # 成果总数+1
        self.pro_sum += 1
        self.save(update_fields=['pro_sum'])

    def pro_sum_cut(self):
        # 成果总数-1
        if self.pro_sum > 0:
            self.pro_sum -= 1
        else:
            self.pro_sum = 0
        self.save(update_fields=['pro_sum'])


class ProRelations(models.Model):
    """
    成果与参与人员小组关系表
    """
    ROLES_CHOICES = ((1, '组长'), (2, '副组长'), (3, '组员'))
    id = models.AutoField(primary_key=True, verbose_name='ID')
    pro = models.ForeignKey(Projects, on_delete=models.CASCADE, verbose_name='成果id')
    par = models.ForeignKey(Participant, on_delete=models.CASCADE, verbose_name='参与人员id')
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name='机构id', null=True)
    roles = models.IntegerField(choices=ROLES_CHOICES, verbose_name='课题组内角色', null=True)
    score = models.FloatField(verbose_name='评价指数', default=1)
    speciality = models.CharField(max_length=50, verbose_name='业务专长', null=True)
    job = models.CharField(max_length=50, verbose_name='职务职称', null=True)
    task = models.CharField(max_length=200, verbose_name='课题组内承担的任务', null=True)
    is_eft = models.BooleanField(default=0, verbose_name='是否有效')


class UserBehavior(models.Model):
    """用户行为信息表"""
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户ID", null=True)
    keyword = models.CharField(max_length=100, verbose_name="用户行为关键词", null=False)
    search_con = models.TextField(verbose_name='行为条件', null=False)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='搜索时间', editable=False)

    class Meta:
        verbose_name_plural = '用户行为数据表'


class UserClickBehavior(models.Model):
    """用户浏览行为信息表"""
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户ID", null=True)
    pro = models.ForeignKey(Projects, on_delete=models.CASCADE, verbose_name="成果对应id", null=False)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', editable=False)

    class Meta:
        verbose_name_plural = '用户浏览行为数据表'


class UserDownloadBehavior(models.Model):
    """用户下载行为信息表"""
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户ID", null=True)
    pro = models.ForeignKey(Projects, on_delete=models.CASCADE, verbose_name="成果对应id", null=False)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', editable=False)

    class Meta:
        verbose_name_plural = '用户下载行为数据表'


class RunInfo(models.Model):
    """程序运行警告报错信息表"""
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    level = models.CharField(max_length=10, verbose_name='级别', null=False, default='warn')
    address = models.CharField(max_length=100, verbose_name="追踪路径", null=False)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='发生时间', editable=False)
    user = models.IntegerField(verbose_name="用户ID", null=True)
    keyword = models.TextField(verbose_name="提示关键词", null=False)

    class Meta:
        verbose_name_plural = '程序运行警告报错信息表'


class HotWords(models.Model):
    """热词表"""
    id = models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, editable=False)
    # user = models.CharField(max_length=150, verbose_name="用户名")
    hot_word = models.CharField(max_length=20, verbose_name="热词")
    is_true = models.BooleanField(default=0, verbose_name="是否可用")
    num = models.IntegerField(verbose_name="等级", default=1)
    create_date = models.DateField(auto_now_add=True, verbose_name="创建时间", editable=False)

    class Meta:
        verbose_name_plural = '热词表'
        ordering = ('-create_date',)


class SensitiveWords(models.Model):
    """敏感词表"""
    id = models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, editable=False)
    sen_word = models.CharField(max_length=20, verbose_name="敏感词")
    is_true = models.BooleanField(default=1, verbose_name="是否可用")
    level = models.IntegerField(verbose_name="等级", default=1)
    create_date = models.DateField(auto_now_add=True, verbose_name="创建时间", editable=False)

    class Meta:
        verbose_name_plural = '敏感词表'
        ordering = ('-create_date',)


class LimitNums(models.Model):
    """查重阈值表"""
    # id = models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, editable=False)
    limit_word = models.FloatField(verbose_name="阈值")
    is_true = models.BooleanField(default=1, verbose_name="是否可用")
    level = models.IntegerField(verbose_name="等级", default=1)
    create_date = models.DateField(auto_now_add=True, verbose_name="创建时间", editable=False)

    class Meta:
        verbose_name = "查重阈值表"
        verbose_name_plural = "查重阈值表"

    # """
    #     如果有__unicode__ 方法，将会优先调用，没有在调用__str__方法
    # """
    #
    # def __unicode__(self):
    #     return '部门' + self.name
    #
    # def __str__(self):
    #     return self.name


class User(AbstractUser):
    org = models.ForeignKey(Organization, verbose_name="机构关联", on_delete=models.CASCADE, null=True)
    par = models.ForeignKey(Participant, verbose_name="人员关联", on_delete=models.CASCADE, null=True)
    id_card = models.CharField(verbose_name="社会信用码/身份证号", max_length=18, null=True)
    cell_phone = models.CharField(max_length=11, verbose_name="手机号", null=True)
    certification_materials = models.CharField(max_length=100, verbose_name="证明材料", null=True)  # 从注册表拷贝路径过来
    photo = models.ImageField(upload_to='user/portrait/%Y/%m', verbose_name='头像', null=True)
    submitter = models.ForeignKey(to='self', verbose_name="提交用户", on_delete=models.CASCADE, null=True)  # 自关联记录是谁创建了这个用户

    class Meta:
        verbose_name_plural = '用户信息表'


class UserRegister(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, editable=False)
    roles = models.IntegerField(verbose_name="角色", null=False)  # 2100：机构管理员用户 4200：个人用户
    username = models.CharField(max_length=20, verbose_name="用户名", null=False)
    id_card_code = models.CharField(max_length=18, verbose_name="社会信用码/身份证号", null=True)
    name = models.CharField(max_length=100, verbose_name="名称", null=True)
    cell_phone = models.CharField(max_length=11, verbose_name="手机号", null=False)
    login_pwd = models.CharField(max_length=10, verbose_name="登录密码", null=False)
    certification_materials = models.FileField(verbose_name="证明材料", null=True,
                                               upload_to='register/materials/%Y/%m')
    verification_code_photo = models.ImageField(verbose_name="验证码图片", null=True,
                                                upload_to='register/verify_code/%Y/%m')
    verification_code = models.CharField(max_length=5, verbose_name="验证码", null=True)
    email = models.CharField(max_length=100, verbose_name="邮箱", null=True)
    create_date = models.DateField(auto_now_add=True, verbose_name="创建时间", editable=False)
    info_status = models.IntegerField(verbose_name="状态", null=False, default=0)  # 1：通过 2：否决  0：未处理
    remarks = models.TextField(verbose_name="备注", null=True)  # 备注

    class Meta:
        verbose_name = "注册表"
        verbose_name_plural = "注册表"


class BidEvaluation(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, editable=False)
    relate_bid = models.ForeignKey(Bid, on_delete=models.CASCADE, null=False, verbose_name='对应投标')
    designated_experts = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True, verbose_name='指定专家')
    operate_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='操作账号')
    result = models.IntegerField(verbose_name="评审结果", null=False, default=0)  # 1通过、2否决、0无
    stage = models.CharField(max_length=10, verbose_name="阶段", null=False, default="立项")  # 立项、立项终审、中期、验收、验收终审
    remarks = models.TextField(verbose_name="备注", null=True)
    evaluate_attached = models.FileField(verbose_name="附件", null=True, upload_to='bid_evaluation/%Y/%m')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    operate_time = models.DateTimeField(null=True, verbose_name="专家操作时间")
    is_show = models.BooleanField(default=1, verbose_name="是否显示")

    class Meta:
        verbose_name = "课题评审表-针对投标小课题"


class News(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, editable=False)
    title = models.CharField(max_length=300, null=False, verbose_name='新闻标题')
    is_show = models.BooleanField(verbose_name="是否显示", null=False, default=1)
    text_attached = models.FileField(verbose_name="正文附件", null=True, upload_to='news/text_part/%Y/%m')
    image_attached = models.FileField(verbose_name="图片附件", null=True, upload_to='news/image/%Y/%m')
    text_create_time = models.DateTimeField(verbose_name="正文发布时间", null=False)  # 用户自行选择
    image_create_time = models.DateTimeField(verbose_name="图片上传时间", null=True)  # 用户自行选择

    class Meta:
        verbose_name = "新闻管理"


class UserToParticipant(models.Model):
    """
    研究人员验证表
    """
    GENDER_CHOICES = ((1, '男'), (2, '女'))
    id = models.AutoField(primary_key=True, verbose_name='ID')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户", null=False)
    gender = models.IntegerField(choices=GENDER_CHOICES, verbose_name='性别', default=1)
    birth = models.DateField(null=True, verbose_name='出生日期')
    education = models.CharField(max_length=100, null=True, verbose_name="本人最高学历")
    academic_degree = models.CharField(max_length=100, null=True, verbose_name="本人学位")
    address = models.TextField(null=True, verbose_name="地址")
    postcode = models.IntegerField(null=True, verbose_name="邮编")
    brief = models.TextField(null=True, verbose_name='简介')
    research_direction = models.CharField(max_length=100, verbose_name='专长', null=True)
    photo = models.ImageField(upload_to='participants/portrait/%Y/%m', verbose_name='头像', null=True)
    id_card_photo_positive = models.ImageField(upload_to='participants/id_card/%Y/%m', verbose_name='身份证正面', null=True)
    id_card_photo_reverse = models.ImageField(upload_to='participants/id_card/%Y/%m', verbose_name='身份证反面', null=True)
    job_certi = models.FileField(upload_to='participants/job_certi/%Y/%m', verbose_name='在职证明', null=True)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True)
    approval_date = models.DateTimeField(verbose_name='审批时间', null=True)
    up_status = models.IntegerField(verbose_name='状态', default=0)  # 0:待审批 1：通过 2：驳回
    remarks = models.TextField(verbose_name='审批备注', null=True)

    class Meta:
        verbose_name_plural = '研究人员验证表'


class ParRePro(models.Model):
    """
    研究人员认证成果表
    """
    id = models.AutoField(primary_key=True, verbose_name='ID')
    par = models.ForeignKey(Participant, on_delete=models.CASCADE, verbose_name="研究人员", null=False)
    pro = models.ForeignKey(Projects, on_delete=models.CASCADE, verbose_name="成果", null=False)
    support_materials = models.FileField(upload_to='participants/tovip/%Y/%m', verbose_name='证明材料', null=True)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name_plural = '研究人员认证成果表'


class ParToVIP(models.Model):
    """
    研究人员升级专家vip认证表
    """
    id = models.AutoField(primary_key=True, verbose_name='ID')
    par = models.ForeignKey(Participant, on_delete=models.CASCADE, verbose_name="研究人员", null=False)
    level = models.IntegerField(verbose_name="vip级别", default=2)
    result = models.IntegerField(verbose_name='结果', default=0)  # 0：待审批 1：通过 2：驳回
    remarks = models.TextField(null=True, verbose_name='备注')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', null=True)
    approval_date = models.DateTimeField(verbose_name='审批时间', null=True)

    class Meta:
        verbose_name_plural = '研究人员升级专家vip认证表'
