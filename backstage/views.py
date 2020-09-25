from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import Group
from tables import models
from jsg import settings
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from backstage.split_pages import split_page
from query.split_page import SplitPages
from uploads.read_pdf import pdf2txtmanager
import datetime
import os
import time
import json
from rest_framework.authtoken.models import Token
from login.views import set_run_info


def add_user_behavior(keyword: str, search_con: str, user_obj=None):
    """
    添加行为记录
    :param keyword: 关键词, 不为空
    :param search_con: 内容，不为空
    :param user_obj: 对象，为空时是游客
    :return:
    """
    models.UserBehavior.objects.create(user=user_obj, keyword=keyword, search_con=search_con)


def create_dirs_not_exist(path):
    """
    判断目录是否存在,不存在就创建
    """
    if not os.path.exists(path):
        os.makedirs(path)


def file_name_is_exits(path, file_obj):
    """
    判断文件是否重名
    :param path: 文件绝对路径
    :param file_obj: 文件对象
    :return: 不重复的文件绝对路径
    """
    current_time = time.strftime('%H%M%S')
    current_year = datetime.datetime.now().year
    current_month = '{:02d}'.format(datetime.datetime.now().month)

    # 成果上传保存路径
    pro_save_path_dirs = os.path.join(
        os.path.join(os.path.join(settings.MEDIA_ROOT, 'attached'), str(current_year)),
        current_month)
    if os.path.exists(path):
        (filename, extension) = os.path.splitext(file_obj.name)
        attached_name = '{}_{}{}'.format(filename, current_time, extension)
        path = os.path.join(pro_save_path_dirs, attached_name)
    else:
        attached_name = file_obj.name

    return path, attached_name


# 分权限
def get_user_permission(user):
    """
    区分管理员与普通人员
    :param user: 登录对象
    :return: user_permission-查看等级，1：所有数据可操作 0：只能看自己的数据
    """
    group_id_obj = Group.objects.filter(user=user.id)
    # 属于多个组的，取最小id（权限最大）
    group_id_list = [i.id for i in group_id_obj]
    if group_id_list:
        user_group_id = min(group_id_list)
    else:
        user_group_id = 0
    if user.is_superuser or user_group_id == 1 or user_group_id == 2:
        user_permission = 1
    else:
        user_permission = 0
    org_id = 0
    if not user_permission:
        org_id = user.org.id
    print('org_id', org_id, 'user_group_id', user_group_id, 'user_permission', user_permission)
    return {"user_permission": user_permission, "org_id": org_id}


@csrf_exempt
def user_login(request):
    """
    用户登录及其验证
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login_manage/page-login.html')
    else:
        print(request.POST)
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user:
            models.User.objects.filter(username=username).update(back_is_login=1)
            login(request, user)
            request.session['user_id'] = user.id  # 退出登录用，前后端同时退出
            group_id_obj = Group.objects.filter(user=user.id)
            # 属于多个组的，取最小id（权限最大）
            group_id_list = [i.id for i in group_id_obj]
            if group_id_list:
                request.session['group_id'] = min(group_id_list)
            if user.first_name:
                request.session['nickname'] = user.first_name
            else:
                request.session['nickname'] = user.username

            add_user_behavior(keyword='', search_con='用户登录', user_obj=user)
            return HttpResponse(1)
        else:
            return HttpResponse(0)


def login_out(request):
    """
    用户退出
    :param request:
    :return:
    """
    if request.session.get('group_id'):
        del request.session['group_id']
    if request.session.get('nickname'):
        del request.session['nickname']
    if request.session.get('user_id'):
        user_id = request.session.get('user_id')
        user = models.User.objects.filter(id=user_id)
        add_user_behavior(keyword='', search_con='用户退出', user_obj=user[0])
        user.update(back_is_login=0)
        Token.objects.filter(user_id=user_id).delete()
    if request.session.get('org_level'):
        del request.session['org_level']
    logout(request)
    # return HttpResponse(1)
    return redirect('/back/to_start_screen/')
    # return render(request, 'login_manage/page-login.html')


# 判断是否登录--用于前端随时检测后台登录情况
def get_login_status(request):
    user_id = request.GET.get('userid', 0)
    res = models.User.objects.get(id=user_id).back_is_login
    print(res)
    return HttpResponse(res)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def main(request):
    user = request.user
    print('user', user)
    user_permission_dict = get_user_permission(user)
    # user_id = user.id
    # print('11111111', user_id)
    # 成果总数--合格的
    pro_sum_obj = models.Projects.objects.filter(status=1)
    # 课题招标总数--招标中的
    res_sum_obj = models.Research.objects.filter(status=1)
    # 推进中的课题量
    res_ing_sum_obj = models.Bid.objects.filter(bidder_status__in=[1, 2], conclusion_status=0)
    # 课题结题量
    res_ed_sum_obj = models.Bid.objects.filter(conclusion_status__in=[1, 2])
    # 研究人员量
    par_sum_obj = models.Participant.objects
    # 研究机构总数
    org_sum_obj = models.Organization.objects
    # 用户总数
    user_sum_obj = models.User.objects
    user_daily_sum = 0

    if not user_permission_dict['user_permission']:
        pro_sum_obj = pro_sum_obj.filter(user__org=user_permission_dict['org_id'])
        res_sum_obj = res_sum_obj.filter(user__org=user_permission_dict['org_id'])
        res_ing_sum_obj = res_ing_sum_obj.filter(submitter__org=user_permission_dict['org_id'])
        res_ed_sum_obj = res_ed_sum_obj.filter(submitter__org=user_permission_dict['org_id'])
        par_sum_obj = par_sum_obj.filter(unit=user_permission_dict['org_id'])
        org_sum_obj = org_sum_obj.filter(id=user_permission_dict['org_id'])
        user_sum_obj = user_sum_obj.filter(org=user_permission_dict['org_id'])
    else:
        # 今日用户访问
        current_date = time.strftime('%Y-%m-%d')
        user_daily_obj = models.UserBehavior.objects.values('user_id').filter(
            create_time__gte=current_date, user__isnull=False).distinct('user_id')
        user_daily_sum = user_daily_obj.count()

    pro_sum = pro_sum_obj.count()
    res_sum = res_sum_obj.count()
    res_ing_sum = res_ing_sum_obj.count()
    res_ed_sum = res_ed_sum_obj.count()
    par_sum = par_sum_obj.count()
    org_sum_obj = org_sum_obj.count()
    user_sum_obj = user_sum_obj.count()

    res = {'pro_sum': pro_sum, 'res_sum': res_sum, 'res_ing_sum': res_ing_sum, 'user_sum': user_sum_obj,
           'res_ed_sum': res_ed_sum, 'par_sum': par_sum, 'org_sum': org_sum_obj, 'user_daily_sum': user_daily_sum}
    return render(request, 'index.html', {'data': res})


def get_daily_login_user(request):
    # 今日用户访问
    current_date = time.strftime('%Y-%m-%d')
    user_obj = models.UserBehavior.objects.values('user_id').filter(
        create_time__gte=current_date, user__isnull=False).distinct('user_id')
    user_obj_list = [i['user_id'] for i in user_obj]
    user_daily_obj = models.User.objects.values('username', 'first_name').filter(id__in=user_obj_list)
    return render(request, 'user_manage/user/check_user_login.html', {'data': user_daily_obj})


# 成果管理
def get_org_str(pro_uuid: str, org_name: str):
    # 获得多对多字段机构名称
    org_name_list = []
    org_id_list = []
    data = models.Projects.objects.get(uuid=pro_uuid)
    if org_name == 'lead_org':
        org_obj = data.lead_org.all()
    else:
        org_obj = data.research.all()
    # print(research_org)
    if org_obj:
        org_name_list = [i.name for i in org_obj]
        org_id_list = [str(i.id) for i in org_obj]
    org_name_str = ''
    org_id_str = ''
    if org_name_list:
        org_name_str = ';'.join(org_name_list)
        org_id_str = ';'.join(org_id_list)
    return org_name_str, org_id_str


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def projects_manage(request):
    """
    成果管理
    :param request:
    :return:
    """
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword', '')
    # status=5 删除状态
    data = models.Projects.objects.values('uuid', 'name', 'classify__cls_name', 'key_word',
                                          'status', 'user__first_name').exclude(status=5).order_by('-id')
    if keyword:
        data = data.filter(Q(name__contains=keyword) | Q(key_word__contains=keyword))
        # -- 记录开始 --
        add_user_behavior(keyword=keyword, search_con='搜索成果信息：{}'.format(str(data.query)), user_obj=request.user)
        # -- 记录结束 --
    # -- 权限开始 --
    user = request.user
    user_permission_dict = get_user_permission(user)
    if not user_permission_dict['user_permission']:
        data = data.filter(user__org=user_permission_dict['org_id'])
    # -- 权限结束 --

    for i in range(len(data)):
        if data[i]['status'] in [0, 2, 3, 4]:
            data[i]['edit'] = 1
        else:
            data[i]['edit'] = 0

        data[i]['status'] = settings.PROJECTS_STATUS_CHOICE[data[i]['status']]

    # -- 分页开始 --
    data = split_page(page, 7, data, 10)
    # print(data)
    # -- 分页结束 --

    return render(request, 'data_manage/projects/projects.html', {"data": data, "keyword": keyword})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def pro_add(request):
    """
    添加成果
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'data_manage/projects/project_add.html')
    elif request.method == 'POST':
        print(request.POST)
        print(request.FILES)
        param_dict = request.POST
        bt = param_dict.get('bt', 0)
        name = param_dict.get('name')
        bid = param_dict.get('bid_id')
        lead_org_id_str = param_dict.get('lead_org_id_str')
        research_id_str = param_dict.get('research_id_str')
        classify = param_dict.get('classify')
        key_word = param_dict.get('key_word')
        abstract = param_dict.get('abstract')
        reference = param_dict.get('reference')
        attached = request.FILES.get('attached')

        if int(bt):
            status = 3
            current_date = time.strftime('%Y-%m-%d')
            release_date = current_date
        else:
            status = 2
            release_date = None

        if bid:
            bid_obj = models.Bid.objects.get(id=bid)
        else:
            bid_obj = None
        # print()
        # ------研发人员信息--------
        par_id_list = param_dict.getlist('par_id')
        job_list = param_dict.getlist('job')
        roles_list = param_dict.getlist('roles')

        try:
            print('attached_path', attached, type(attached))

            if attached:
                # 上传文件操作  setting/MEDIA.ROOT
                # 判断目录是否存在,不存在就创建
                current_year = datetime.datetime.now().year
                current_month = '{:02d}'.format(datetime.datetime.now().month)

                # 成果上传保存路径
                pro_save_path_dirs = os.path.join(
                    os.path.join(os.path.join(settings.MEDIA_ROOT, 'attached'), str(current_year)),
                    current_month)
                create_dirs_not_exist(pro_save_path_dirs)
                # 保存的路径
                save_path = os.path.join(pro_save_path_dirs, attached.name)
                # 判断文件是否存在, 避免重名
                save_path, attached_name_fin = file_name_is_exits(save_path, attached)
                print('save_path', save_path)
                # 在保存路径下，建立文件
                with open(save_path, 'wb') as f:
                    # 在f.chunks()上循环保证大文件不会大量使用你的系统内存
                    for content in attached.chunks():
                        f.write(content)

                content = read_con(save_path)

                pro_obj = models.Projects.objects.create(
                    name=name,
                    classify=models.Classify.objects.get(pk=classify),
                    key_word=key_word,
                    abstract=abstract,
                    reference=reference,
                    status=status,
                    release_date=release_date,
                    user=request.user,
                    bid=bid_obj,
                    text_part=content,
                    attached="attached/{}/{}/{}".format(current_year, current_month, attached_name_fin)
                )
            else:
                pro_obj = models.Projects.objects.create(
                    name=name,
                    classify=models.Classify.objects.get(pk=classify),
                    key_word=key_word,
                    abstract=abstract,
                    reference=reference,
                    status=status,
                    release_date=release_date,
                    user=request.user,
                    bid=bid_obj
                )

            print('***', pro_obj, type(pro_obj))

            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='添加成果:{}'.format(str(pro_obj.id)), user_obj=request.user)
            # -- 记录结束 --

            # 多对多对象创建
            if lead_org_id_str:
                lead_org_id_list = lead_org_id_str.split(';')
                print('&&&', lead_org_id_list)
                lead_org_id_list_obj = models.Organization.objects.filter(id__in=lead_org_id_list)
                pro_obj.lead_org.add(*lead_org_id_list_obj)

            if research_id_str:
                research_id_list = research_id_str.split(';')
                print(research_id_list)
                research_id_list_obj = models.Organization.objects.filter(id__in=research_id_list)
                pro_obj.research.add(*research_id_list_obj)

            # 添加课题小组信息
            if par_id_list:
                for i in range(len(par_id_list)):
                    par_obj = models.Participant.objects.get(id=par_id_list[i])
                    models.ProRelations.objects.create(is_eft=False, par=par_obj, org=par_obj.unit, pro=pro_obj,
                                                       job=job_list[i], roles=roles_list[i])
            return HttpResponse(200)
        except Exception as e:
            set_run_info(level='error', address='/backstage/view.py/pro_add',
                         user=request.user.id, keyword='添加成果失败：{}'.format(e))
            return HttpResponse(400)


def read_con(path):
    """
    读取pdf文件
    :param path:
    :return:
    """
    content = ''
    try:
        content = pdf2txtmanager.pdf2text(path)
    except Exception as e:
        set_run_info(level='error', address='/uploads/view.py/ProjectsUploadView-read_con',
                     keyword='读取pdf文件失败：{}'.format(e))
    return content


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def project_edit(request, uuid):
    """
    成果编辑
    :param request:
    :param uuid: 成果唯一标识
    :return:
    """
    # data = get_object_or_404(models.Projects, uuid=uuid)
    data = models.Projects.objects.values('id', 'uuid', 'name', 'classify', 'key_word', 'release_date',
                                          'status', 'attached', 'bid__re_title', 'bid__id').filter(uuid=uuid)
    print(data)
    obj = data[0]
    obj['lead_org'], obj['lead_org_id'] = get_org_str(uuid, 'lead_org')
    obj['research'], obj['research_id'] = get_org_str(uuid, 'research')
    # 课题小组信息
    par_id_obj = models.ProRelations.objects.values('par__id', 'par__name', 'roles', 'job', 'org__name').filter(
        pro=obj['id'], par__id__isnull=False).order_by('roles')
    return render(request, 'data_manage/projects/projects_edit.html', {"data": obj, "par_org": par_id_obj})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def project_edit_do(request):
    """
    成果编辑提交
    :param request:
    :return:
    """
    print(request.POST)
    print(request.FILES)
    param_dict = request.POST
    bt = param_dict.get('bt', 0)
    name = param_dict.get('name')
    uuid = param_dict.get('uuid')
    bid = param_dict.get('bid_id')
    lead_org_id_str = param_dict.get('lead_org_id_str')
    research_id_str = param_dict.get('research_id_str')
    classify = param_dict.get('classify')
    key_word = param_dict.get('key_word')
    abstract = param_dict.get('abstract')
    reference = param_dict.get('reference')
    release_date = param_dict.get('release_date')
    attached = request.FILES.get('attached')

    pro_obj = models.Projects.objects.filter(uuid=uuid)

    if int(bt):
        status = 3
        if release_date == 'None' or release_date is None:
            current_date = time.strftime('%Y-%m-%d')
            release_date = current_date
    else:
        status = 2
        if release_date == 'None' or release_date is None:
            release_date = None

    if release_date.find('年'):
        release_date = release_date.replace('年', '-').replace('月', '-').replace('日', '')

    # ------研发人员信息--------
    par_id_list = param_dict.getlist('par_id')
    # print(par_id, type(par_id))
    job_list = param_dict.getlist('job')
    roles_list = param_dict.getlist('roles')
    try:
        if par_id_list:
            for i in range(len(par_id_list)):
                pro_relation_obj = models.ProRelations.objects.filter(pro=pro_obj[0].id, par=par_id_list[i])
                if pro_relation_obj:
                    pro_relation_obj.update(job=job_list[i], roles=roles_list[i])
                else:
                    par_obj = models.Participant.objects.get(id=par_id_list[i])
                    models.ProRelations.objects.create(is_eft=False, par=par_obj, org=par_obj.unit, pro=pro_obj[0],
                                                       job=job_list[i], roles=roles_list[i])

        # 多对多对象删除
        pro_obj[0].lead_org.clear()
        pro_obj[0].research.clear()

        # 多对多对象创建
        if lead_org_id_str:
            lead_org_id_list = lead_org_id_str.split(';')
            print('&&&', lead_org_id_list)
            lead_org_id_list_obj = models.Organization.objects.filter(id__in=lead_org_id_list)
            pro_obj[0].lead_org.add(*lead_org_id_list_obj)

        if research_id_str:
            research_id_list = research_id_str.split(';')
            print(research_id_list)
            research_id_list_obj = models.Organization.objects.filter(id__in=research_id_list)
            pro_obj[0].research.add(*research_id_list_obj)

        print('attached_path', attached, type(attached))
        print('---', release_date)
        if attached:
            current_year = datetime.datetime.now().year
            current_month = '{:02d}'.format(datetime.datetime.now().month)

            # 成果上传保存路径
            pro_save_path_dirs = os.path.join(
                os.path.join(os.path.join(settings.MEDIA_ROOT, 'attached'), str(current_year)),
                current_month)
            # 重新上传文件操作  setting/MEDIA.ROOT
            # 判断目录是否存在,不存在就创建
            create_dirs_not_exist(pro_save_path_dirs)
            # 保存的路径
            save_path = os.path.join(pro_save_path_dirs, attached.name)
            # 判断文件是否存在, 避免重名
            save_path, attached_name_fin = file_name_is_exits(save_path, attached)
            print('save_path', save_path)
            # 在保存路径下，建立文件
            with open(save_path, 'wb') as f:
                # 在f.chunks()上循环保证大文件不会大量使用你的系统内存
                for content in attached.chunks():
                    f.write(content)

            pro_obj.update(
                name=name,
                classify=classify,
                key_word=key_word,
                abstract=abstract,
                reference=reference,
                status=status,
                release_date=release_date,
                bid=bid,
                attached="attached/{}/{}/{}".format(current_year, current_month, attached_name_fin)
            )
        else:
            pro_obj.update(
                name=name,
                classify=classify,
                key_word=key_word,
                abstract=abstract,
                reference=reference,
                status=status,
                bid=bid,
                release_date=release_date,
            )
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='修改成果信息：{};{}'.format(str(request.POST), str(attached)),
                          user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(200)
    except Exception as e:
        # print(e)
        set_run_info(level='error', address='/backstage/view.py/project_edit_do',
                     user=request.user.id, keyword='修改成果失败：{}'.format(e))
        return HttpResponse(400)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def project_detail(request):
    """
    成果详情
    :param request:
    :return:
    """
    print('aaaaa', request.GET)
    uuid = request.GET.get('uuid')
    if uuid:
        data = models.Projects.objects.filter(uuid=uuid)
        if data:

            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='查看成果信息：{}'.format(uuid),
                              user_obj=request.user)
            # -- 记录结束 --

            obj = data.values('id', 'uuid', 'name', 'classify__cls_name', 'key_word', 'bid__re_title', 'attached',
                              'downloads', 'views', 'user__username', 'release_date', 'status', 'update_date')
            obj = obj[0]
            obj['lead_org'] = get_org_str(uuid, 'lead_org')[0]
            obj['research'] = get_org_str(uuid, 'research')[0]
            obj['status'] = settings.PROJECTS_STATUS_CHOICE[obj['status']]
            obj['key_word'] = str(obj['key_word']).replace(' ', '\n')
            # data['reference'] = str(data['reference']).replace(';', '\n')

            # 课题小组信息
            par_id_obj = models.ProRelations.objects.values('par__name', 'roles', 'job', 'org__name').filter(
                pro=obj['id'], par__id__isnull=False).order_by('roles')
            for i in range(len(par_id_obj)):
                par_id_obj[i]['roles'] = settings.PRO_RELATIONS_ROLES[par_id_obj[i]['roles']]
            # return JsonResponse({"data": obj, "par_org": list(par_id_obj), "code": 200})
            print(obj)
            return render(request, 'data_manage/projects/projects_detail2.html',
                          {"data": obj, "par_org": list(par_id_obj), "code": 200})
        else:
            return render(request, 'data_manage/projects/projects_detail2.html',
                          {"data": list(), "par_org": list(), "code": 404})
    else:
        return render(request, 'data_manage/projects/projects_detail2.html',
                      {"data": list(), "par_org": list(), "code": 403})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def project_del(request):
    """
    成果删除--假删除，设置为删除状态, 发布成功不可删除
    :param request:
    :return:
    """
    uuid = request.POST.get('uuid')
    pro_obj = models.Projects.objects.filter(uuid=uuid)
    if pro_obj:
        result = pro_obj.update(status=5)
        pro_obj_id = pro_obj[0].id
        models.ProRelations.objects.filter(pro=pro_obj_id).update(is_eft=False)
        print(result)
        if result == 1:
            # 直接写路由
            # return redirect('/back/pm')
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='删除成果信息：{}'.format(uuid), user_obj=request.user)
            # -- 记录结束 --
            return HttpResponse(1)
        else:
            return HttpResponse(0)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def project_withdraw(request):
    """
    成果撤回 -将合格状态转化为待完善状态
    :param
    request:
    :return:
    """
    uuid = request.POST.get('uuid')
    try:
        pro_obj = models.Projects.objects.filter(uuid=uuid)
        pro_obj.update(status=2)
        pro_obj_id = pro_obj[0].id
        # 作废关系
        par_pro_obj = models.ProRelations.objects.filter(pro=pro_obj_id)
        par_pro_obj.update(is_eft=False)
        for par_obj in par_pro_obj:
            par_obj.par.pro_sum_cut()
        # 减少各机构的成果总量
        lead_org_obj = pro_obj[0].lead_org.all()
        research_obj = pro_obj[0].research.all()
        queryset_list = []
        queryset_list.extend(lead_org_obj)
        queryset_list.extend(research_obj)
        queryset_list = list(set(queryset_list))
        for i in queryset_list:
            i.pro_sum_cut()

        # 直接写路由
        # return redirect('/back/pm')
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='撤回成果：{}'.format(uuid), user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(1)
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/project_withdraw',
                     user=request.user.id, keyword='成果撤回失败：{}'.format(e))
        return HttpResponse(0)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def pro_relations_del(request):
    """
    成果删除课题小组人员-关系表删除--真删除
    :param request:
    :return:
    """
    par_id = request.POST.get('par_id')
    pro_uuid = request.POST.get('pro_uuid')
    try:
        pro_id = models.Projects.objects.get(uuid=pro_uuid)
        print(pro_id, par_id)
        models.ProRelations.objects.filter(par=par_id, pro=pro_id).delete()
        # -- 记录开始 --
        add_user_behavior(keyword='',
                          search_con='成果-课题小组人员删除：成果（{}），人员（{}）'.format(pro_uuid, par_id),
                          user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(1)
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/pro_relations_del',
                     user=request.user.id, keyword='成果删除课题小组人员失败：{}'.format(e))
        return HttpResponse(0)


@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def project_sp(request):
    """
    成果审批
    :param request:
    :return:
    """
    if request.method == 'GET':
        his = request.GET.get('his', '')  # his有值的时候，为查看成果审批历史操作
        page = request.GET.get('page', 1)
        keyword = request.GET.get('keyword', '')
        if his:
            # status=1 合格 4 不合格
            data = models.Projects.objects.values('uuid', 'name', 'classify__cls_name', 'status', 'user__first_name'
                                                  ).filter(status__in=[1, 4]).order_by('-id')
            if keyword:
                data = data.filter(Q(name__contains=keyword) | Q(lead_org__name__contains=keyword))

            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='查看成果审批记录', user_obj=request.user)
            # -- 记录结束 --

            for i in range(len(data)):
                if data[i]['status'] == 1:
                    data[i]['status'] = '通过'
                else:
                    data[i]['status'] = '驳回'
                data[i]['lead_org'] = get_org_str(data[i]['uuid'], 'lead_org')[0]
                data[i]['research'] = get_org_str(data[i]['uuid'], 'research')[0]
            # -- 分页开始 --
            data = split_page(page, 7, data, 10)
            # print(data)
            # -- 分页结束 --
            return render(request, 'data_manage/projects/projects_sp_his.html', {'data': data, 'keyword': keyword})
        else:
            # status=3 待审批
            data = models.Projects.objects.values('uuid', 'name', 'classify__cls_name', 'attached', 'user__first_name'
                                                  ).filter(status=3).order_by('-id')
            if keyword:
                data = data.filter(Q(name__contains=keyword) | Q(lead_org__name__contains=keyword))

            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='查看成果待审批项', user_obj=request.user)
            # -- 记录结束 --

            for i in range(len(data)):
                data[i]['lead_org'] = get_org_str(data[i]['uuid'], 'lead_org')[0]
                data[i]['research'] = get_org_str(data[i]['uuid'], 'research')[0]
            # -- 分页开始 --
            data = split_page(page, 7, data, 10)
            # print(data)
            # -- 分页结束 --
            return render(request, 'data_manage/projects/projects_sp.html', {'data': data, 'keyword': keyword})

    elif request.method == 'POST':
        print(request.POST)
        uuid = request.POST.get('uuid')
        status = request.POST.get('status')  # 同意1还是驳回4
        try:
            status = int(status)
            pro_obj = models.Projects.objects.filter(uuid=uuid)
            pro_obj.update(status=status)
            if status == 1:
                lead_org_obj = pro_obj[0].lead_org.all()
                research_obj = pro_obj[0].research.all()
                queryset_list = []
                queryset_list.extend(lead_org_obj)
                queryset_list.extend(research_obj)
                queryset_list = list(set(queryset_list))
                for i in queryset_list:
                    i.pro_sum_add()
                par_pro_obj = models.ProRelations.objects.filter(pro=pro_obj[0])
                par_pro_obj.update(is_eft=True)
                for par_obj in par_pro_obj:
                    par_obj.par.pro_sum_add()
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='审批成果:{},{}'.format(uuid, str(status)), user_obj=request.user)
            # -- 记录结束 --
            return HttpResponse(1)
        except Exception as e:
            set_run_info(level='error', address='/backstage/view.py/project_sp',
                         user=request.user.id, keyword='成果审批失败：{}'.format(e))
            return HttpResponse(0)


@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def good_project_manage(request):
    """
    优秀成果管理
    :param request:
    :return:
    """
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        keyword = request.GET.get('keyword')
        mark_id = request.GET.get('mark_id')
        # tag = request.GET.get('tag')

        data = models.Projects.objects.values('uuid', 'name', 'classify__cls_name', 'key_word', 'good_mark__remarks',
                                              'release_date', 'user__first_name').filter(status=1).order_by('-id')
        if keyword:
            data = data.filter(Q(name__contains=keyword) | Q(key_word__contains=keyword))
            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='搜索优秀成果信息：{}'.format(str(data.query)), user_obj=request.user)
            # -- 记录结束 --

        pro_mark = models.ProjectsMark.objects.all().order_by('-level')

        # if tag:
        #     data = data.filter(good_mark__isnull=True)
        # else:
        if mark_id:
            data = data.filter(good_mark=mark_id)
        else:
            if pro_mark:
                mark_id = pro_mark[0].id
                data = data.filter(good_mark=mark_id)

        # -- 分页开始 --
        data = split_page(page, 7, data, 10)
        # print(data)
        # -- 分页结束 --

        # print(pro_mark)
        return render(request, 'data_manage/projects/project_good.html',
                      {"data": data, "keyword": keyword, "pro_mark": pro_mark, "mark_id": int(mark_id)})

    elif request.method == 'POST':
        print(request.POST)
        uuid = request.POST.get('uuid')
        mark_id = request.POST.get('mark_id', None)  # 若能获取到mark_id,则代表选中，若没有则代表撤销
        try:
            uuid_list = uuid.split(';')
            pro_obj = models.Projects.objects.filter(uuid__in=uuid_list)
            pro_obj.update(good_mark=mark_id)
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='优秀成果管理:{},{}'.format(uuid, str(mark_id)), user_obj=request.user)
            # -- 记录结束 --
            return HttpResponse(1)
        except Exception as e:
            set_run_info(level='error', address='/backstage/view.py/good_project_manage-post',
                         user=request.user.id, keyword='优秀成果管理失败：{}'.format(e))
            return HttpResponse(0)


def choose_good_project_manage(request):
    """
    选择优秀成果
    :param request:
    :return:
    """
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        keyword = request.GET.get('keyword')

        data = models.Projects.objects.values('uuid', 'name', 'release_date', 'user__first_name'
                                              ).filter(status=1).order_by('-id')
        if keyword:
            data = data.filter(Q(name__contains=keyword) | Q(key_word__contains=keyword))
            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='搜索优秀成果信息：{}'.format(str(data.query)), user_obj=request.user)
            # -- 记录结束 --

        data = data.filter(good_mark__isnull=True)

        # -- 分页开始 --
        # sp = SplitPages(data, page, 10)
        # res = sp.split_page()
        # print(data)
        # -- 分页结束 --

        # print(pro_mark)
        return JsonResponse({"data": list(data), "keyword": keyword})


# 课题管理
@login_required(login_url='/back/to_start_screen/')
def research_manage(request):
    """
    招标管理
    :param request:
    :return:
    """
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword', '')
    data = models.Research.objects.values('id', 'uuid', 'name', 'classify__cls_name', 'funds', 'start_date', 'end_date',
                                          'status', 'user__username').exclude(status=4).order_by('-id')

    if keyword:
        data = data.filter(Q(name__contains=keyword) | Q(funds__contains=keyword) | Q(start_date__contains=keyword) | Q(
            start_date__contains=keyword))

        # -- 记录开始 --
        add_user_behavior(keyword=keyword, search_con='搜索招标信息', user_obj=request.user)
        # -- 记录结束 --

    # -- 权限开始 --
    user = request.user
    user_permission_dict = get_user_permission(user)
    if not user_permission_dict['user_permission']:
        data = data.filter(user__org=user_permission_dict['org_id'])
    # -- 权限结束 --

    for i in range(len(data)):
        if data[i]['status'] == 0:
            data[i]['edit'] = 1
        else:
            data[i]['edit'] = 0
        # 统计投标数量
        bid_count = models.Bid.objects.filter(bidder_status=1, bidding=data[i]['id']).count()
        data[i]['bid_count'] = bid_count
        # 统计申请结题数量
        bid_conclusion = models.Bid.objects.filter(conclusion_status=1, bidding=data[i]['id']).count()
        data[i]['bid_conclusion'] = bid_conclusion
        # 将状态改为对应含义
        data[i]['status'] = settings.RESEARCH_STATUS_CHOICE[data[i]['status']]

    # -- 分页开始 --
    data = split_page(page, 7, data, 10)
    # print(data)
    # -- 分页结束 --

    return render(request, 'data_manage/research/research.html', {"data": data, "keyword": keyword})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def research_edit(request, uuid):
    """
    课题编辑
    :param request:
    :param uuid: 课题唯一标识
    :return:
    """
    data = models.Research.objects.values(
        'uuid', 'name', 'classify', 'funds', 'brief', 'start_date', 'end_date', 'contacts',
        'phone', 'guidelines', 'status').filter(uuid=uuid)
    if data:
        data = data[0]
        data['start_date'] = str(data['start_date'])
        data['end_date'] = str(data['end_date'])
    # print(type(data['start_date']))
    return render(request, 'data_manage/research/research_edit.html', {"data": data})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def research_edit_do(request):
    """
    课题编辑提交
    :param request:
    :return:
    """
    print(request.POST)
    print(request.FILES)
    param_dict = request.POST
    name = param_dict.get('name')
    uuid = param_dict.get('uuid')
    start_date = param_dict.get('start_date')
    end_date = param_dict.get('end_date')
    classify = param_dict.get('classify')
    funds = param_dict.get('funds')
    brief = param_dict.get('brief')
    contacts = param_dict.get('contacts')
    phone = param_dict.get('phone')
    bt = param_dict.get('bt')
    guidelines = request.FILES.get('guidelines')
    print('attached_path', guidelines, type(guidelines))
    try:
        bt = int(bt)
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/research_edit_do',
                     user=request.user.id, keyword='课题信息编辑-bt参数转化失败：{}'.format(e))
        bt = 0
    if bt:
        # 点击提交
        status = 1
    else:
        # 点击保存
        status = 0
    try:
        if guidelines:
            current_year = datetime.datetime.now().year
            current_month = '{:02d}'.format(datetime.datetime.now().month)
            re_save_path_dirs = os.path.join(
                os.path.join(os.path.join(settings.MEDIA_ROOT, 'guide'), str(current_year)),
                current_month)
            # 重新上传文件操作  setting/MEDIA.ROOT
            # 判断目录是否存在,不存在就创建
            create_dirs_not_exist(re_save_path_dirs)
            # 保存的路径
            save_path = os.path.join(re_save_path_dirs, guidelines.name)
            # 判断文件是否存在, 避免重名
            save_path, attached_name_fin = file_name_is_exits(save_path, guidelines)
            print('save_path', save_path)
            # 在保存路径下，建立文件
            with open(save_path, 'wb') as f:
                # 在f.chunks()上循环保证大文件不会大量使用你的系统内存
                for content in guidelines.chunks():
                    f.write(content)

            models.Research.objects.filter(uuid=uuid).update(
                name=name,
                start_date=start_date,
                end_date=end_date,
                classify=classify,
                funds=funds,
                brief=brief,
                contacts=contacts,
                phone=phone,
                status=status,
                guidelines="guide/{}/{}/{}".format(current_year, current_month, attached_name_fin)
            )
        else:
            models.Research.objects.filter(uuid=uuid).update(
                name=name,
                start_date=start_date,
                end_date=end_date,
                classify=classify,
                funds=funds,
                brief=brief,
                contacts=contacts,
                phone=phone,
                status=status
            )
        # -- 记录开始 --
        add_user_behavior(keyword='',
                          search_con='修改招标信息:{},{}'.format(str(param_dict), str(guidelines)),
                          user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(200)
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/research_edit_do',
                     user=request.user.id, keyword='课题信息编辑失败：{}'.format(e))
        return HttpResponse(400)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def research_add(request):
    """
    发布招标
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'data_manage/research/research_add.html')
    elif request.method == 'POST':
        print(request.POST)
        print(request.FILES)
        param_dict = request.POST
        name = param_dict.get('name')
        start_date = param_dict.get('start_date')
        end_date = param_dict.get('end_date')
        classify = param_dict.get('classify')
        funds = param_dict.get('funds')
        brief = param_dict.get('brief')
        contacts = param_dict.get('contacts')
        phone = param_dict.get('phone')
        bt = param_dict.get('bt')
        guidelines = request.FILES.get('guidelines')
        print('attached_path', guidelines, type(guidelines))
        if funds == '':
            funds = 0
        try:
            bt = int(bt)
        except Exception as e:
            set_run_info(level='error', address='/backstage/view.py/research_add',
                         user=request.user.id, keyword='招标发布-bt参数转化失败：{}'.format(e))
            bt = 0
        if bt:
            # 点击提交
            status = 1
        else:
            # 点击保存
            status = 0
        try:
            if guidelines:
                # 重新上传文件操作  setting/MEDIA.ROOT
                current_year = datetime.datetime.now().year
                current_month = '{:02d}'.format(datetime.datetime.now().month)
                re_save_path_dirs = os.path.join(
                    os.path.join(os.path.join(settings.MEDIA_ROOT, 'guide'), str(current_year)),
                    current_month)
                # 判断目录是否存在,不存在就创建
                create_dirs_not_exist(re_save_path_dirs)
                # 保存的路径
                save_path = os.path.join(re_save_path_dirs, guidelines.name)
                # 判断文件是否存在, 避免重名
                save_path, attached_name_fin = file_name_is_exits(save_path, guidelines)
                print('save_path', save_path)
                # 在保存路径下，建立文件
                with open(save_path, 'wb') as f:
                    # 在f.chunks()上循环保证大文件不会大量使用你的系统内存
                    for content in guidelines.chunks():
                        f.write(content)

                re_obj = models.Research.objects.create(
                    name=name,
                    start_date=start_date,
                    end_date=end_date,
                    classify=models.Classify.objects.get(pk=classify),
                    funds=funds,
                    brief=brief,
                    contacts=contacts,
                    phone=phone,
                    status=status,
                    user=request.user,
                    guidelines="guide/{}/{}/{}".format(current_year, current_month, attached_name_fin)
                )
            else:
                re_obj = models.Research.objects.create(
                    name=name,
                    start_date=start_date,
                    end_date=end_date,
                    classify=models.Classify.objects.get(pk=classify),
                    funds=funds,
                    brief=brief,
                    contacts=contacts,
                    phone=phone,
                    status=status,
                    user=request.user
                )
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='添加招标信息:（{}）'.format(str(re_obj.id)),
                              user_obj=request.user)
            # -- 记录结束 --
            return HttpResponse(200)
        except Exception as e:
            set_run_info(level='error', address='/backstage/view.py/research_add',
                         user=request.user.id, keyword='招标发布失败：{}'.format(e))
            return HttpResponse(400)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def research_detail(request):
    """
    课题详情
    :param request:
    :return:
    """
    print('aaaaa', request.GET)
    uuid = request.GET.get('uuid')
    if uuid:
        data = models.Research.objects.values(
            'uuid', 'name', 'classify__cls_name', 'funds', 'brief', 'start_date', 'end_date', 'contacts', 'phone',
            'guidelines', 'status', 'user__username').filter(uuid=uuid)
        if data:
            data = data[0]
            data['status'] = settings.RESEARCH_STATUS_CHOICE[data['status']]
            # return JsonResponse({"data": data, "code": 200})
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='查看招标详情:{}'.format(uuid), user_obj=request.user)
            # -- 记录结束 --
            return render(request, 'data_manage/research/research_detail2.html', {"data": data, "code": 200})

        else:
            # return JsonResponse({"data": '', "code": 404})
            return render(request, 'data_manage/research/research_detail2.html', {"data": list(), "code": 404})
    else:
        return render(request, 'data_manage/research/research_detail2.html', {"data": list, "code": 403})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def research_del(request):
    """
    课题删除--假删除，设置为删除状态
    :param request:
    # :param uuid:
    :return:
    """
    uuid = request.POST.get('uuid')
    try:
        models.Research.objects.filter(uuid=uuid).update(status=4)
        # 直接写路由
        # return redirect('/back/pm')
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='删除招标信息:{}'.format(uuid), user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(1)
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/research_del',
                     user=request.user.id, keyword='设置课题删除状态失败：{}'.format(e))
        return HttpResponse(0)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def research_bid_manage(request):
    """
    管理投标列表
    :param request:
    :return:
    """
    # print('user', request.user)
    if request.method == 'GET':
        # 获取投标列表
        re_id = request.GET.get('id')
        print(re_id)
        re_name = models.Research.objects.values('name').filter(pk=re_id)
        if re_name:
            re_name = re_name[0]['name']
        else:
            re_name = ''
        print(re_name, type(re_name))
        data = models.Bid.objects.values(
            'id', 're_title', 'bidder_date', 'bidder_status', 'bidder', 'leader', 'lea_phone',
            'contacts', 'con_phone').filter(bidder_status=1, bidding=re_id).order_by('-id')
        print('data', data)
        # -- 记录开始 --
        # add_user_behavior(keyword='', search_con='获取招标对应投标列表:{}'.format(re_id), user_obj=request.user)
        # -- 记录结束 --
        return JsonResponse({"data": list(data), "re_name": re_name, "code": 200})

    elif request.method == 'POST':
        # 批量同意/驳回
        print(request.POST)
        param_dict = request.POST
        id_list_str = param_dict.get('id_list')
        is_true = param_dict.get('is_true')
        id_list = json.loads(id_list_str)
        print(id_list)
        if int(is_true) == 1:
            bid_obj = models.Bid.objects.filter(id__in=id_list)
            result = bid_obj.update(bidder_status=2)
            for i_obj in bid_obj:
                if i_obj.bidding.status == 1:
                    models.Research.objects.filter(id=i_obj.bidding.id).update(status=2)
        else:
            result = models.Bid.objects.filter(id__in=id_list).update(bidder_status=3)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='批量同意/驳回招标对应投标信息:{}'.format(str(param_dict)), user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(result)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def research_bid_jt_manage(request):
    """
    申请结题管理列表
    :param request:
    :return:
    """
    # print('user', request.user)
    if request.method == 'GET':
        # 获取投标列表
        re_id = request.GET.get('id')
        print(re_id)
        re_name = models.Research.objects.values('name').filter(pk=re_id)
        if re_name:
            re_name = re_name[0]['name']
        else:
            re_name = ''
        print(re_name, type(re_name))
        data = models.Bid.objects.values(
            'id', 're_title', 'bidder_date', 'bidder_status', 'bidder', 'leader', 'lea_phone',
            'contacts', 'con_phone').filter(conclusion_status=1, bidding=re_id).order_by('-id')
        print('data', data)
        # -- 记录开始 --
        # add_user_behavior(keyword='', search_con='获取招标对应投标结题申请列表:{}'.format(re_id), user_obj=request.user)
        # -- 记录结束 --
        return JsonResponse({"data": list(data), "re_name": re_name, "code": 200})

    elif request.method == 'POST':
        # 批量同意/驳回
        print(request.POST)
        param_dict = request.POST
        id_list_str = param_dict.get('id_list')
        is_true = param_dict.get('is_true')
        id_list = json.loads(id_list_str)
        # print(id_list)
        # result=1
        if int(is_true) == 1:
            bid_obj = models.Bid.objects.filter(id__in=id_list)
            result = bid_obj.update(conclusion_status=2)
            for i_obj in bid_obj:
                print(i_obj.bidding.id)
                con_dict = models.Bid.objects.values('conclusion_status').filter(bidding_id=i_obj.bidding.id,
                                                                                 bidder_status=2)
                con_list = [i['conclusion_status'] for i in con_dict]
                if len(set(con_list)) == 1:
                    models.Research.objects.filter(id=i_obj.bidding.id).update(status=3)
                # print(set(con_list))
                # if i_obj.bidding.status == 1:
                #     models.Research.objects.filter(id=i_obj.bidding.id).update(status=2)
        else:
            result = models.Bid.objects.filter(id__in=id_list).update(conclusion_status=3)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='批量同意/驳回招标对应投标结题申请信息:{}'.format(str(param_dict)),
                          user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(result)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def research_sp_history(request, param):
    """
    申请/结题审批记录
    :param request:
    :return:
    """
    if request.method == 'GET':
        # 获取审批记录
        page = request.GET.get('page', 1)
        keyword = request.GET.get('keyword', '')
        data = models.Bid.objects.values(
            're_title', 'bidder_date', 'bidder_status', 'bidder', 'bidding__name', 'conclusion_status').order_by('-id')
        if keyword:
            data = data.filter(
                Q(re_title__contains=keyword) | Q(bidder_date__contains=keyword) | Q(bidding__name__contains=keyword))
        # -- 权限开始 --
        user = request.user
        user_permission_dict = get_user_permission(user)
        if not user_permission_dict['user_permission']:
            data = data.filter(bidding__user__org=user_permission_dict['org_id'])
        # -- 权限结束 --
        result_status_dict = {2: '通过', 3: '驳回'}
        if param == 'bid':
            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='查看招标申请审批记录', user_obj=request.user)
            # -- 记录结束 --
            data = data.filter(bidder_status__in=[2, 3])
            for i in range(len(data)):
                data[i]['bidder_status'] = result_status_dict[data[i]['bidder_status']]
            # print('data', data)
            # -- 分页开始 --
            data = split_page(page, 7, data, 10)
            # print(data)
            # -- 分页结束 --
            return render(request, 'data_manage/research/research_bid_sp_history.html',
                          {"data": data, "keyword": keyword})
        elif param == 'jt':
            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='查看招标结题审批记录', user_obj=request.user)
            # -- 记录结束 --
            data = data.filter(conclusion_status__in=[2, 3])
            for i in range(len(data)):
                data[i]['conclusion_status'] = result_status_dict[data[i]['conclusion_status']]
            # print('data', data)
            # -- 分页开始 --
            data = split_page(page, 7, data, 10)
            # print(data)
            # -- 分页结束 --
            return render(request, 'data_manage/research/research_jt_sp_history.html',
                          {"data": data, "keyword": keyword})


# 投标管理
# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def bid_manage(request):
    """
    投标管理
    :param request:
    :return:
    """
    # print('user', request.user)
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword', '')
    data = models.Bid.objects.values(
        'id', 'bidding__name', 're_title', 'bidder_date', 'bidder_status',
        'funds', 'contacts', 'con_phone', 'conclusion_status').exclude(bidder_status=4).order_by('-id')

    if keyword:
        data = data.filter(Q(bidding__name__contains=keyword) | Q(re_title__contains=keyword) |
                           Q(bidder_date__contains=keyword) | Q(funds__contains=keyword) | Q(
            contacts__contains=keyword) |
                           Q(con_phone__contains=keyword))

        # -- 记录开始 --
        add_user_behavior(keyword=keyword, search_con='搜索投标信息', user_obj=request.user)
        # -- 记录结束 --

    # -- 权限开始 --
    user = request.user
    user_permission_dict = get_user_permission(user)
    if not user_permission_dict['user_permission']:
        data = data.filter(submitter__org=user_permission_dict['org_id'])
    # -- 权限结束 --

    for i in range(len(data)):
        data[i]['conclusion'] = 0
        data[i]['edit'] = 0
        if data[i]['bidder_status'] == 0 or data[i]['bidder_status'] == 3:
            data[i]['edit'] = 1
        elif data[i]['bidder_status'] == 2:
            if data[i]['conclusion_status'] in [0, 3]:
                data[i]['conclusion'] = 1
        data[i]['bidder_status'] = settings.BIDDER_STATUS_CHOICE[data[i]['bidder_status']]
        data[i]['conclusion_status'] = settings.BIDDER_CONCLUSION_STATUS[data[i]['conclusion_status']]

    # -- 分页开始 --
    data = split_page(page, 7, data, 10)
    # print(data)
    # -- 分页结束 --

    return render(request, 'data_manage/bid/bid.html', {"data": data, "keyword": keyword})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def bid_edit(request, edit_id):
    """
    投标编辑
    :param request:
    :param edit_id: 投标唯一标识
    :return:
    """
    data = models.Bid.objects.values(
        'id', 'funds', 're_title', 'contacts', 'con_phone', 'leader',
        'lea_phone', 'brief').filter(id=edit_id)
    if data:
        data = data[0]
    return render(request, 'data_manage/bid/bid_edit.html', {"data": data})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def bid_edit_do(request):
    """
    投标编辑提交
    :param request:
    :return:
    """
    param_dict = request.POST

    edit_id = param_dict.get('edit_id')
    funds = param_dict.get('funds')
    re_title = param_dict.get('re_title')
    contacts = param_dict.get('contacts')
    con_phone = param_dict.get('con_phone')
    leader = param_dict.get('leader')
    lea_phone = param_dict.get('lea_phone')
    brief = param_dict.get('brief')
    status = param_dict.get('bbt')
    current_date = time.strftime('%Y-%m-%d')
    try:
        status = int(status)
    except Exception as e:
        set_run_info(level='warn', address='/backstage/view.py/bid_edit_do',
                     user=request.user.id, keyword='投标信息编辑-status参数转化出错：{}'.format(e))
        status = 0
    if status:
        status = 1
    else:
        status = 0
    try:
        models.Bid.objects.filter(id=edit_id).update(
            re_title=re_title,
            con_phone=con_phone,
            leader=leader,
            funds=funds,
            brief=brief,
            contacts=contacts,
            lea_phone=lea_phone,
            bidder_status=status,
            bidder_date=current_date
        )
        # -- 记录开始 --
        add_user_behavior(keyword='',
                          search_con='修改投标信息({}):{}'.format(edit_id, str(param_dict)),
                          user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(200)
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/bid_edit_do',
                     user=request.user.id, keyword='投标信息编辑失败：{}'.format(e))
        return HttpResponse(400)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def bid_detail(request):
    """
    投标详情
    :param request:
    :return:
    """
    print('aaaaa', request.GET)
    uuid = request.GET.get('uuid')
    single = request.GET.get('single', 0)  # 返回单独的页面标志
    # -- 记录开始 --
    add_user_behavior(keyword='', search_con='查看投标详情({})'.format(uuid), user_obj=request.user)
    # -- 记录结束 --
    if not single:
        if uuid:
            data = models.Bid.objects.values(
                'id', 'bidder', 'bidding__name', 're_title', 'bidder_date', 'bidder_status', 'funds', 'contacts',
                'con_phone', 'leader', 'lea_phone', 'brief', 'submitter__username').filter(id=uuid)
            if data:
                data = data[0]
                data['bidder_status'] = settings.BIDDER_STATUS_CHOICE[data['bidder_status']]
                # return JsonResponse({"data": data, "code": 200})
                return render(request, 'data_manage/bid/bid_detail2.html', {"data": data, "code": 200})
            else:
                # return JsonResponse({"data": '', "code": 404})
                return render(request, 'data_manage/bid/bid_detail2.html', {"data": list(), "code": 404})
        else:
            return render(request, 'data_manage/bid/bid_detail2.html', {"data": list(), "code": 403})
    else:
        if uuid:
            data = models.Bid.objects.values(
                'id', 'bidder', 'bidding__name', 're_title', 'bidder_date', 'bidder_status', 'funds', 'contacts',
                'con_phone', 'leader', 'lea_phone', 'brief', 'submitter__username').filter(id=uuid)
            if data:
                data = data[0]
                # data['bidder_status'] = settings.BIDDER_STATUS_CHOICE[data['bidder_status']]
                return render(request, 'data_manage/bid/bid_detail_single.html', {"data": data})
            else:
                return JsonResponse({"data": '', "code": 404})
        else:
            return JsonResponse({"code": 403, "data": ''})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def bid_del(request):
    """
    投标删除--假删除，设置为删除状态
    :param request:
    # :param uuid:
    :return:
    """
    uuid = request.POST.get('uuid')
    try:
        models.Bid.objects.filter(id=uuid).update(bidder_status=4)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='删除投标信息({})'.format(uuid), user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(1)
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/bid_del',
                     user=request.user.id, keyword='投标信息设置删除状态失败：{}'.format(e))
        return HttpResponse(0)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def bid_apply_conclusion(request):
    """
    申请结题
    :param request:
    :return:
    """
    uuid = request.POST.get('uuid')
    try:
        models.Bid.objects.filter(id=uuid).update(conclusion_status=1)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='投标申请结题({})'.format(uuid), user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(1)
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/bid_apply_conclusion',
                     user=request.user.id, keyword='投标信息申请结题失败：{}'.format(e))
        return HttpResponse(0)


@login_required(login_url='/back/to_start_screen/')
def bid_search(request):
    """
    投标搜索
    :param request:
    :return:
    """
    keyword = request.GET.get('keyword', '')
    print(request.user.org)
    data = models.Bid.objects.values('id', 're_title', 'bidder_date').filter(
        bidder_status=2, submitter__org=request.user.org)
    if keyword:
        # 用作搜索
        data = data.filter(re_title__contains=keyword).order_by('-id')
        print(data.query)
        return JsonResponse({"data": list(data), "code": 200})
    else:
        data = data.order_by('-id')
        return JsonResponse({"data": list(data), "code": 200})


# 研究人员管理
# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def participant_manage(request):
    """
    研究人员管理
    :param request:
    :return:
    """
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword', '')
    data = models.Participant.objects.values('uuid', 'name', 'unit__name', 'job', 'email').exclude(is_show=0).order_by(
        '-id')
    if keyword:
        data = data.filter(Q(name__contains=keyword) | Q(unit__name__contains=keyword) |
                           Q(job__contains=keyword) | Q(email__contains=keyword))
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='搜索研究人员信息', user_obj=request.user)
        # -- 记录结束 --

    # -- 权限开始 --
    user = request.user
    user_permission_dict = get_user_permission(user)
    if not user_permission_dict['user_permission']:
        data = data.filter(unit=user_permission_dict['org_id'])
    # -- 权限结束 --
    # -- 分页开始 --
    data = split_page(page, 7, data, 10)
    # print(data)
    # -- 分页结束 --
    return render(request, 'user_manage/participant/participant.html', {"data": data, "keyword": keyword})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def participant_edit(request, uuid):
    """
    研究人员编辑
    :param request:
    :param uuid: 研究人员唯一标识
    :return:
    """
    data = models.Participant.objects.values(
        'uuid', 'name', 'gender', 'unit__name', 'job', 'email', 'brief', 'photo'
    ).filter(uuid=uuid)
    if data:
        data = data[0]
        print(data['gender'])
    return render(request, 'user_manage/participant/participant_edit.html', {"data": data})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def participant_edit_do(request):
    """
    研究人员编辑提交
    :param request:
    :return:
    """
    print(request.POST)
    param_dict = request.POST
    uuid = param_dict.get('uuid')
    name = param_dict.get('name')
    gender = param_dict.get('gender')
    # unit = param_dict.get('unit')
    job = param_dict.get('job')
    email = param_dict.get('email')
    brief = param_dict.get('brief')
    photo = request.FILES.get('photo')
    print('participants', photo, type(photo))
    try:
        # -- 记录开始 --
        add_user_behavior(keyword='',
                          search_con='修改研究人员信息({}):{}'.format(uuid, str(param_dict)),
                          user_obj=request.user)
        # -- 记录结束 --
        if photo:
            # 重新上传文件操作  setting/MEDIA.ROOT
            save_path_dirs = os.path.join(os.path.join(settings.MEDIA_ROOT, 'participants'))
            # 判断目录是否存在,不存在就创建
            # create_dirs_not_exist(save_path_dirs)
            # 保存的路径
            save_path = os.path.join(save_path_dirs, photo.name)
            # 判断文件是否存在, 避免重名
            current_time = time.strftime('%H%M%S')
            if os.path.exists(save_path):
                (filename, extension) = os.path.splitext(photo.name)
                attached_name = '{}_{}.{}'.format(filename, current_time, extension)
                save_path = os.path.join(save_path_dirs, attached_name)
            print('save_path', save_path)
            # 在保存路径下，建立文件
            with open(save_path, 'wb') as f:
                # 在f.chunks()上循环保证大文件不会大量使用你的系统内存
                for content in photo.chunks():
                    f.write(content)

            models.Participant.objects.filter(uuid=uuid).update(
                name=name,
                gender=gender,
                # unit=unit,
                job=job,
                email=email,
                brief=brief,
                photo="participants/{}".format(photo.name)
            )
            # 直接写路由
            return redirect('/back/parm')
        else:
            models.Participant.objects.filter(uuid=uuid).update(
                name=name,
                gender=gender,
                # unit=unit,
                job=job,
                email=email,
                brief=brief,
            )
            return redirect('/back/parm')
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/participant_edit_do',
                     user=request.user.id, keyword='研究人员信息编辑失败：{}'.format(e))
        return HttpResponse('编辑失败')


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def participant_detail(request):
    """
    研究人员详情
    :param request:
    :return:
    """
    print('aaaaa', request.GET)
    uuid = request.GET.get('uuid')
    if uuid:
        data = models.Participant.objects.values(
            'uuid', 'name', 'gender', 'unit__name', 'job', 'email', 'brief', 'photo', 'pro_sum').filter(uuid=uuid)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='查看研究人员信息详情({})'.format(uuid), user_obj=request.user)
        # -- 记录结束 --
        if data:
            data = data[0]
            if data['gender'] == 1:
                data['gender'] = '男'
            else:
                data['gender'] = '女'
            return JsonResponse({"data": data, "code": 200})
        else:
            return JsonResponse({"data": '', "code": 404})
    else:
        return JsonResponse({"code": 403, "data": ''})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def participant_add(request):
    """
    添加研究人员
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'user_manage/participant/par_add.html')
    elif request.method == 'POST':
        print(request.POST)
        param_dict = request.POST
        name = param_dict.get('name')
        name = name.replace(' ', '')  # 去除空格
        org_uuid = param_dict.get('org-uuid')
        org_name = param_dict.get('unit')
        gender = param_dict.get('gender')
        email = param_dict.get('email')
        job = param_dict.get('job')
        brief = param_dict.get('brief')
        photo = request.FILES.get('photo')

        org_name = org_name.replace(' ', '')
        org_obj_list = models.Organization.objects.filter(uuid=org_uuid, name=org_name)
        if org_obj_list:
            org_obj = org_obj_list[0]
            org_obj.par_sum_add()
            # print(group_obj_list)
        else:
            # 机构不存在
            return HttpResponse(404)

        try:
            par_obj = models.Participant.objects.create(
                name=name,
                job=job,
                photo=photo,
                unit=org_obj,
                brief=brief,
                gender=gender,
                email=email,
                is_show=True
            )
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='创建研究人员信息({})'.format(par_obj.id), user_obj=request.user)
            # -- 记录结束 --
            return HttpResponse(201)
        except Exception as e:
            set_run_info(level='error', address='/backstage/view.py/participant_add',
                         user=request.user.id, keyword='创建研究人员信息失败：{}'.format(e))
            return HttpResponse(500)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def participant_del(request):
    """
    研究人员删除--假删除，设置为删除状态
    :param request:
    # :param uuid:
    :return:
    """
    uuid = request.POST.get('uuid')
    try:
        data = models.Participant.objects.filter(uuid=uuid)
        data.update(is_show=0)
        if data[0].unit:
            data[0].unit.par_sum_cut()
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='删除研究人员信息({})'.format(uuid), user_obj=request.user)
        # -- 记录结束 --
        # print(result)
        return HttpResponse(1)
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/participant_del',
                     user=request.user.id, keyword='设置研究人员信息删除状态失败：{}'.format(e))
        return HttpResponse(0)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def participant_search(request):
    """
    研究人员搜索
    :param request:
    :return:
    """
    # print('aaaaa', request.GET)
    keyword = request.GET.get('keyword', '')
    par_id = request.GET.get('id', '')

    if keyword:
        # 用作搜索
        data = models.Participant.objects.values(
            'id', 'name', 'unit__name', 'job').filter(is_show=True).filter(
            Q(name__contains=keyword) | Q(unit__name__contains=keyword) | Q(job__contains=keyword))
        # -- 记录开始 --
        add_user_behavior(keyword=keyword, search_con='成果添加课题小组成员-搜索研究人员信息-根据关键词', user_obj=request.user)
        # -- 记录结束 --
        return JsonResponse({"data": list(data), "code": 200})
    elif par_id:
        # 用作添加--通过id获取姓名和所在单位
        data = models.Participant.objects.values(
            'id', 'name', 'unit__name', 'job').filter(id=par_id)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='成果添加课题小组成员-获取具体研究人员信息-根据id', user_obj=request.user)
        # -- 记录结束 --
        return JsonResponse({"data": data[0], "code": 200})
    else:
        data = models.Participant.objects.values(
            'id', 'name', 'unit__name', 'job').filter(is_show=True).order_by('-id')
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='成果添加课题小组成员-获取所有研究人员信息', user_obj=request.user)
        # -- 记录结束 --
        return JsonResponse({"data": list(data), "code": 200})


# 用户管理
# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def user_manage(request):
    """
    机构用户管理
    :param request:
    :return:
    """
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword', '')
    data = models.User.objects.values('id', 'username', 'first_name', 'is_active').order_by('-id')
    if keyword:
        data = data.filter(Q(username__contains=keyword) | Q(first_name__contains=keyword))

        # -- 记录开始 --
        add_user_behavior(keyword=keyword, search_con='搜索用户信息', user_obj=request.user)
        # -- 记录结束 --

    # -- 权限开始 --
    user = request.user
    user_permission_dict = get_user_permission(user)
    is_manage = 1
    if not user_permission_dict['user_permission']:
        is_manage = 0
        data = data.filter(org=user_permission_dict['org_id'])
    # -- 权限结束 --
    # -- 分页开始 --
    data = split_page(page, 7, data, 10)
    # print(data)
    # -- 分页结束 --
    return render(request, 'user_manage/user/user.html', {"data": data, "keyword": keyword, 'is_manage': is_manage})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def user_add(request):
    """
    新增用户
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'user_manage/user/user_add.html')
    elif request.method == 'POST':
        print(request.POST)
        param_dict = request.POST
        username = param_dict.get('username')
        first_name = param_dict.get('first_name')
        password = param_dict.get('password')
        org_uuid = param_dict.get('org-uuid')
        org_name = param_dict.get('org')
        is_manage = int(param_dict.get('is_manage'))
        groups_list = []

        if is_manage:
            # 添加管理员组
            groups_list.append(2)

        if not first_name:
            # 如果没有昵称，则默认显示机构名称
            first_name = org_name

        org_name = org_name.replace(' ', '')
        org_obj_list = models.Organization.objects.filter(uuid=org_uuid, name=org_name)
        if org_obj_list:
            org_obj = org_obj_list[0]
            if org_obj.is_a:
                # 添加甲方组
                groups_list.append(3)
            if org_obj.is_b:
                # 添加乙方组
                groups_list.append(4)
            # print(group_obj_list)
        else:
            # 机构不存在
            return HttpResponse(404)

        password_end = make_password(password, None, 'pbkdf2_sha256')  # 源字符串，固定字符串，加密方式
        try:
            models.User.objects.create(
                first_name=first_name,
                username=username,
                password=password_end,
                org=org_obj,
            )
            # 添加组
            user_obj = models.User.objects.get(username=username)
            groups_list_obj = Group.objects.filter(id__in=groups_list)
            user_obj.groups.add(*groups_list_obj)

            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='新增用户信息({})'.format(user_obj.id), user_obj=request.user)
            # -- 记录结束 --

            return HttpResponse(201)
        except Exception as e:
            # 创建失败
            set_run_info(level='error', address='/backstage/view.py/user_add',
                         user=request.user.id, keyword='新增用户信息失败：{}'.format(e))
            return HttpResponse(400)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def user_edit(request, uuid):
    """
    用户编辑
    :param request:
    :param uuid: 用户唯一标识
    :return:
    """
    data = models.User.objects.values(
        'id', 'username', 'first_name', 'is_active', 'org__name', 'is_superuser', 'org__uuid').filter(id=uuid)
    is_manage = 0
    if data[0]['is_superuser']:
        is_manage = 1
    else:
        groups = models.User.objects.get(id=uuid).groups.all()
        group_id_list = [i.id for i in groups]
        if group_id_list:
            user_group_id = min(group_id_list)
        else:
            user_group_id = 0
        if user_group_id == 2:
            is_manage = 1
    if data:
        data = data[0]
    # --判断登录用户等级--
    user = request.user
    user_level = 0
    if user.is_superuser:
        user_level = 1
    else:
        if request.session.get('group_id') == 2:
            user_level = 1
    return render(request, 'user_manage/user/user_edit.html',
                  {"data": data, "is_manage": is_manage, 'user_level': user_level})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def user_edit_do(request):
    """
    用户编辑提交
    :param request:
    :return:
    """
    print(request.POST)
    param_dict = request.POST
    uuid = param_dict.get('uuid')
    first_name = param_dict.get('first_name')
    is_active = param_dict.get('is_active')
    org_uuid = param_dict.get('org_uuid')
    org_name = param_dict.get('org')
    is_manage = int(param_dict.get('is_manage'))

    if is_manage:
        models.User.objects.get(id=uuid).groups.add(2)
    else:
        models.User.objects.get(id=uuid).groups.remove(2)

    try:
        org_name = org_name.replace(' ', '')
        org_obj_list = models.Organization.objects.filter(uuid=org_uuid, name=org_name)
        if not org_obj_list:
            # 机构不存在
            return HttpResponse(404)

        models.User.objects.filter(id=uuid).update(
            first_name=first_name,
            is_active=is_active,
            org=org_obj_list[0].id
        )
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='编辑用户信息({}):{}'.format(uuid, str(param_dict)), user_obj=request.user)
        # -- 记录结束 --
        # 直接写路由
        # return redirect('/back/user')
        return HttpResponse(1)
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/user_edit_do',
                     user=request.user.id, keyword='编辑用户信息失败：{}'.format(e))
        return HttpResponse(0)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def user_detail(request):
    """
    用户详情
    :param request:
    :return:
    """
    print('aaaaa', request.GET)
    uuid = request.GET.get('uuid')
    if uuid:
        data = models.User.objects.values(
            'id', 'username', 'first_name', 'org__name', 'date_joined', 'last_login').filter(id=uuid)
        if data:
            data = data[0]
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='查看用户信息详情({})'.format(uuid),
                              user_obj=request.user)
            # -- 记录结束 --
            return JsonResponse({"data": data, "code": 200})
        else:
            return JsonResponse({"data": '', "code": 404})
    else:
        return JsonResponse({"code": 403, "data": ''})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def user_del(request):
    """
    用户禁用或者开启，设置状态
    :param request:
    # :param uuid:
    :return:
    """
    uuid = request.POST.get('uuid')
    tag = int(request.POST.get('tag'))
    if tag == 1:
        result = models.User.objects.filter(id=uuid).update(is_active=True)
    else:
        result = models.User.objects.filter(id=uuid).update(is_active=False)
    # print(result)
    if result == 1:
        # 直接写路由
        # return redirect('/back/pm')
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='禁用/开启用户({}):{}'.format(uuid, tag), user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(1)
    else:
        return HttpResponse(0)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def user_org_search(request):
    """
    新建用户-认证机构，机构检索推荐的时候
    :param request:
    :return:
    """
    keyword = request.GET.get('input_keyword', '')
    print(keyword)
    data = models.Organization.objects.values('uuid', 'name').filter(is_show=True).order_by('-id')
    if keyword:
        data = data.filter(name__contains=keyword)[:15]
        return JsonResponse({'data': list(data)})
    else:
        return JsonResponse({'data': []})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def user_username_search(request):
    """
    新建用户-用户名是否存在验证
    :param request:
    :return:
    """
    username = request.GET.get('username', '')
    # print(username)
    data = models.User.objects.filter(username=username)
    if data:
        return HttpResponse(200)
    else:
        return HttpResponse(404)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def user_modify_password(request, uuid):
    """
    用户修改密码
    :param request:
    :param uuid:
    :return:
    """
    if request.method == 'GET':
        data = models.User.objects.values('id').get(id=uuid)
        return render(request, 'user_manage/user/user_update_pwd.html', {"data": data})
    elif request.method == 'POST':
        param_dict = request.POST
        new_pwd = param_dict.get('new_pwd')
        new_pwd_confirm = param_dict.get('new_pwd_confirm')
        if new_pwd != new_pwd_confirm:
            return HttpResponse(2)
        try:
            user = models.User.objects.get(id=uuid)
            user.set_password(new_pwd)
            user.save()
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='修改用户密码({})'.format(uuid), user_obj=request.user)
            # -- 记录结束 --
            return HttpResponse(1)
        except Exception as e:
            set_run_info(level='error', address='/backstage/view.py/user_modify_password',
                         user=request.user.id, keyword='修改用户密码失败：{}'.format(e))
            return HttpResponse(0)


# 机构管理
@login_required(login_url='/back/to_start_screen/')
def org_manage(request):
    """
    机构管理
    :param request:
    :return:
    """
    page = request.GET.get('page', 1)
    keyword = request.GET.get('keyword', '')
    data = models.Organization.objects.values('uuid', 'name', 'is_a', 'is_b', 'nature__remarks').filter(
        is_show=True).order_by('-id')

    # -- 权限开始 --
    user = request.user
    user_permission_dict = get_user_permission(user)
    if not user_permission_dict['user_permission']:
        data = data.filter(id=user_permission_dict['org_id'])
    # -- 权限结束 --

    if keyword:
        data = data.filter(Q(name__contains=keyword) | Q(nature__remarks__contains=keyword))

        # -- 记录开始 --
        add_user_behavior(keyword=keyword, search_con='搜索机构信息', user_obj=request.user)
        # -- 记录结束 --

    # -- 分页开始 --
    data = split_page(page, 7, data, 10)
    # print(data)
    # -- 分页结束 --
    return render(request, 'user_manage/org/org.html', {"data": data, "keyword": keyword})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def org_add(request):
    """
    添加机构
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'user_manage/org/org_add.html')
    elif request.method == 'POST':
        print(request.POST)
        param_dict = request.POST
        name = param_dict.get('name')
        nature = int(param_dict.get('nature'))
        is_a = param_dict.get('is_a', 0)
        is_b = param_dict.get('is_b', 0)
        brief = param_dict.get('brief')
        photo = request.FILES.get('photo')

        name = name.replace(' ', '')  # 去除空格
        org_obj = models.Organization.objects.filter(name=name)
        if org_obj:
            # 机构名已经存在
            return HttpResponse(2)
        else:
            nature_obj = models.OrgNature.objects.get(pk=nature)
            try:
                new_org_obj = models.Organization.objects.create(
                    name=name,
                    nature=nature_obj,
                    is_a=is_a,
                    is_b=is_b,
                    brief=brief,
                    is_show=True,
                    photo=photo
                )
                # -- 记录开始 --
                add_user_behavior(keyword='', search_con='添加机构信息({})'.format(new_org_obj.id), user_obj=request.user)
                # -- 记录结束 --
                return HttpResponse(1)
            except Exception as e:
                set_run_info(level='error', address='/backstage/view.py/org_add',
                             user=request.user.id, keyword='添加机构信息失败：{}'.format(e))
                return HttpResponse(0)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
@csrf_exempt
def org_del(request):
    """
    机构删除--假删除，设置为删除状态
    :param request:
    # :param uuid:
    :return:
    """
    uuid = request.POST.get('uuid')
    try:
        models.Organization.objects.filter(uuid=uuid).update(is_show=False)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='设置机构信息删除状态({})'.format(uuid), user_obj=request.user)
        # -- 记录结束 --
        return HttpResponse(1)
    except Exception as e:
        set_run_info(level='error', address='/backstage/view.py/org_del',
                     user=request.user.id, keyword='设置机构信息删除状态失败：{}'.format(e))
        return HttpResponse(0)


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def org_edit(request, uuid):
    """
    机构编辑
    :param request:
    :param uuid: 用户唯一标识
    :return:
    """
    if request.method == 'GET':
        data = models.Organization.objects.values('uuid', 'nature', 'is_a', 'is_b', 'brief', 'name', 'photo').filter(
            uuid=uuid)
        if data:
            data = data[0]
        # --判断登录用户等级--
        user = request.user
        user_level = 0
        if user.is_superuser:
            user_level = 1
        else:
            if request.session.get('group_id') == 2:
                user_level = 1
        return render(request, 'user_manage/org/org_edit.html', {"data": data, "user_level": user_level})
    elif request.method == 'POST':
        print(request.POST)
        param_dict = request.POST
        name = param_dict.get('name')
        nature = int(param_dict.get('nature'))
        is_a = param_dict.get('is_a', 0)
        is_b = param_dict.get('is_b', 0)
        brief = param_dict.get('brief')
        photo = request.FILES.get('photo')
        try:
            if photo:
                # 重新上传文件操作  setting/MEDIA.ROOT
                save_path_dirs = os.path.join(os.path.join(settings.MEDIA_ROOT, 'organizations'))
                # 保存的路径
                save_path = os.path.join(save_path_dirs, photo.name)
                # 判断文件是否存在, 避免重名
                current_time = time.strftime('%H%M%S')
                if os.path.exists(save_path):
                    (filename, extension) = os.path.splitext(photo.name)
                    attached_name = '{}_{}.{}'.format(filename, current_time, extension)
                    save_path = os.path.join(save_path_dirs, attached_name)
                print('save_path', save_path)
                # 在保存路径下，建立文件
                with open(save_path, 'wb') as f:
                    # 在f.chunks()上循环保证大文件不会大量使用你的系统内存
                    for content in photo.chunks():
                        f.write(content)

                models.Organization.objects.filter(uuid=uuid).update(
                    name=name,
                    nature=nature,
                    is_a=is_a,
                    is_b=is_b,
                    brief=brief,
                    photo="organizations/{}".format(photo.name)
                )
            else:
                models.Organization.objects.filter(uuid=uuid).update(
                    name=name,
                    nature=nature,
                    is_a=is_a,
                    is_b=is_b,
                    brief=brief,
                )
            # -- 记录开始 --
            add_user_behavior(keyword='',
                              search_con='修改机构信息({}):{}'.format(uuid, str(param_dict)),
                              user_obj=request.user)
            # -- 记录结束 --
            return redirect('/back/org')
        except Exception as e:
            set_run_info(level='error', address='/backstage/view.py/org_edit',
                         user=request.user.id, keyword='机构信息编辑失败：{}'.format(e))
            return HttpResponse('编辑失败')


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def org_detail(request):
    """
    机构详情
    :param request:
    :return:
    """
    print('aaaaa', request.GET)
    uuid = request.GET.get('uuid')
    if uuid:
        data = models.Organization.objects.values(
            'uuid', 'name', 'is_a', 'is_b', 'nature__remarks', 'brief', 'created_date', 'pro_sum', 'par_sum').filter(
            uuid=uuid)
        if data:
            data = data[0]
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='查看机构信息详情({})'.format(uuid), user_obj=request.user)
            # -- 记录结束 --
            return JsonResponse({"data": data, "code": 200})
        else:
            return JsonResponse({"data": '', "code": 404})
    else:
        return JsonResponse({"code": 403, "data": ''})


# @login_required(login_url='/back/login/')
@login_required(login_url='/back/to_start_screen/')
def org_search(request):
    """
    机构搜索
    :param
    :return
    """
    roles = request.GET.get('roles', '')
    keyword = request.GET.get('keyword', '')
    if roles == 'a':
        data = models.Organization.objects.values('id', 'name', 'nature__remarks').filter(is_show=True, is_a=True)
    else:
        data = models.Organization.objects.values('id', 'name', 'nature__remarks').filter(is_show=True, is_b=True)
    if keyword:
        # 用作搜索
        data = data.filter(Q(name__contains=keyword) | Q(nature__remarks__contains=keyword))
        print(data.query)
        return JsonResponse({"data": list(data), "code": 200})
    else:
        data = data.order_by('-id')
        return JsonResponse({"data": list(data), "code": 200})
