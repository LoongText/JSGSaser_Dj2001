from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
# from tables.models import Projects, Research, ProRelations, UserDownloadBehavior
# from tables.models import User, Bid, Organization, Participant
from tables import models
from django.contrib.auth .models import Group, AnonymousUser
import os
from jsg import settings
from django.http import StreamingHttpResponse
from login.views import set_run_info
import urllib.parse
from login.views import add_user_behavior
from rest_framework.decorators import authentication_classes
from login.auth import ExpiringTokenAuthentication
import time
from django.db.models import Count


@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
def projects_download(request):
    """
    课题下载
    :param request:
    :return:
    """
    if request.method == 'GET':
        uuid = request.query_params.get('uuid', '')
        # user_id = request.query_params.get('userid', 0)
        ways = request.query_params.get('ways', 'v')  # 区分查看还是下载
        user = request.user
        try:
            obj = models.Projects.objects.filter(uuid=uuid)[0]
            if ways == 'd':
                obj.download_num_update()  # 下载量+1
                # if user_id and user_id != 'undefined' and user_id != 'null':
                if type(user) != AnonymousUser:
                    user_obj = models.User.objects.get(id=user.id)
                    models.UserDownloadBehavior.objects.create(user=user_obj, pro=obj)  # 记录下载量数据
                else:
                    models.UserDownloadBehavior.objects.create(pro=obj)  # 记录下载量数据
            # 显示在弹出对话框中的默认的下载文件名
            the_file_name = '{}.pdf'.format(obj.name)
            # print(the_file_name)
            download_url_fin = os.path.join(settings.MEDIA_ROOT, str(obj.attached))
            # 将汉字换成ascii码，否则下载名称不能正确显示
            the_file_name = urllib.parse.quote(the_file_name)
            response = StreamingHttpResponse(file_iterator(download_url_fin))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(the_file_name)

            return response

            # return Response(status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/projects_download',
                         user=user.id, keyword='成果下载失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


# 读取文件
def file_iterator(file_name, chunk_size=512):
    """
    下载文件时读取文件的方法
    :param file_name: 文件绝对路径
    :param chunk_size: 每次循环大小
    :return:
    """
    with open(file_name, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


@api_view(['GET'])
def get_compare_status(request):
    """
    获得成果状态
    :param request:
    :return:
    """
    if request.method == 'GET':
        try:
            uuid = request.query_params.get('uuid', '')
            compare_status = models.Projects.objects.get(uuid=uuid).status
            return Response({"compare_status": compare_status, }, status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/get_compare_status',
                         keyword='获取成果状态失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
def set_pro_status(request):
    # 成果状态设置
    if request.method == 'POST':
        try:
            # print('set_pro_status', request.data)
            param_dict = request.data
            uuid = param_dict.get('uuid', '')
            pro_status = int(param_dict.get('status', 0))
            is_cut_num = int(param_dict.get('is_cut_num', 0))  # 主要区分成果是否发布(目前管理员的删除和撤回都是发布状态，个人发布后不能删除)
            data = models.Projects.objects.filter(uuid=uuid)
            pro_obj_id = data[0].id
            if pro_status == 1:
                data.update(status=pro_status)
                # 增加对应机构成果数
                lead_org_obj = data[0].lead_org.all()
                research_obj = data[0].research.all()
                queryset_list = []
                queryset_list.extend(lead_org_obj)
                queryset_list.extend(research_obj)
                queryset_list = list(set(queryset_list))
                for i in queryset_list:
                    i.pro_sum_add()
                # 将关系置为可用
                par_pro_obj = models.ProRelations.objects.filter(pro=pro_obj_id)
                par_pro_obj.update(is_eft=True)
                # 对应人员成果数+1
                for par_obj in par_pro_obj:
                    par_obj.par.pro_sum_add()
            elif pro_status == 3:
                current_date = time.strftime('%Y-%m-%d')
                data.update(status=pro_status, release_date=current_date)
            else:
                data.update(status=pro_status)
                if is_cut_num:
                    par_pro_obj = models.ProRelations.objects.filter(pro=pro_obj_id)
                    par_pro_obj.update(is_eft=False)
                    # 减少人员和机构的成果量
                    for par_obj in par_pro_obj:
                        par_obj.par.pro_sum_cut()
                    # 减少各机构的成果总量
                    lead_org_obj = data[0].lead_org.all()
                    research_obj = data[0].research.all()
                    queryset_list = []
                    queryset_list.extend(lead_org_obj)
                    queryset_list.extend(research_obj)
                    queryset_list = list(set(queryset_list))
                    for i in queryset_list:
                        i.pro_sum_cut()
            add_user_behavior(keyword='', search_con='修改成果状态：{}'.format(uuid), user_obj=request.user)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/set_pro_status',
                         keyword='修改成果状态失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def file_list(request):
    """
    展示所有文件 home, dirs, files
    :param request:
    :return:
    """
    if request.method == 'GET':
        path = os.path.join(settings.MEDIA_ROOT, 'attached')
        files = os.walk(path)  # home, dirs, files
        return Response({"files": files}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
def set_research_status(request):
    # 招标状态设置
    if request.method == 'POST':
        try:
            # print(request.data)
            param_dict = request.data
            uuid = param_dict.get('uuid', '')
            re_status = int(param_dict.get('status', 0))
            data = models.Research.objects.filter(uuid=uuid)
            if re_status in [0, 1, 2, 3, 4]:
                data.update(status=re_status)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/set_research_status',
                         keyword='修改招标状态失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
def set_bid_status(request):
    # 投标状态设置
    if request.method == 'POST':
        try:
            # print(request.data)
            user = request.user
            if type(user) == AnonymousUser:
                set_run_info(level='error', address='/status_operation/view.py/set_bid_status',
                             keyword='投标状态设置失败：获取不到user')
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                user_id = user.id
            param_dict = request.data
            id_list = param_dict.get('idlist', '')
            bid_status = int(param_dict.get('status', 0))
            tag = param_dict.get('tag', 'sq')  # sq：批量处理申请  jt：批量处理结题  zq:中期
            data = models.Bid.objects.filter(id__in=id_list)
            if tag == 'sq':
                if bid_status in [0, 1, 2, 3, 4, 5, 6]:
                    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                    if bid_status in [2, 3]:
                        # 记录初审通过时间和审批人
                        data.update(bidder_status=bid_status, bid_trial_date=current_time, bid_trial_user=user_id)
                    elif bid_status in [5, 6]:
                        # 记录立项通过时间
                        data.update(bidder_status=bid_status, bid_lix_date=current_time)
                    else:
                        data.update(bidder_status=bid_status)
            elif tag == 'zq':
                if bid_status in [0, 1, 2, 3]:
                    if bid_status in [2, 3]:
                        # 记录中期通过时间
                        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                        data.update(interim_status=bid_status, bid_interim_date=current_time)
                    else:
                        data.update(interim_status=bid_status)
            else:
                if bid_status in [0, 1, 2, 3]:
                    if bid_status in [2, 3]:
                        # 记录结题通过时间
                        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                        data.update(conclusion_status=bid_status, bid_con_date=current_time)
                    else:
                        data.update(conclusion_status=bid_status)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/set_bid_status',
                         keyword='修改投标状态失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
def set_org_status(request):
    # 机构状态设置
    if request.method == 'POST':
        try:
            # print(request.data)
            param_dict = request.data
            uuid_list = param_dict.getlist('uuidlist', '')
            org_status = int(param_dict.get('status', 0))
            models.Organization.objects.filter(uuid__in=uuid_list).update(is_show=org_status)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/set_org_status',
                         keyword='修改机构状态失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
def get_org_name(request):
    # 获得所有机构名称和id:all/获得本机构以及下属机构名称和id:personal
    if request.method == 'GET':
        user = request.user
        if user.is_active:
            try:
                group_id_obj = Group.objects.filter(user=user.id)
                group_id_list = [i.id for i in group_id_obj]
                print('--------', group_id_list)
                if user.is_superuser or settings.SUPER_USER_GROUP in group_id_list or settings.PLANT_MANAGER_GROUP in group_id_list:
                    data = models.Organization.objects.values('id', 'name', 'superior_unit')
                else:
                    user_org = user.org
                    if user_org:
                        org_list = [user_org.id]
                        for org_id in org_list:
                            subordinate_unit_obj = models.Organization.objects.values('id').filter(
                                superior_unit=org_id)
                            subordinate_unit_id = [i['id'] for i in subordinate_unit_obj]
                            org_list.extend(subordinate_unit_id)
                        data = models.Organization.objects.values('id', 'name', 'superior_unit').filter(id__in=org_list)
                    else:
                        # 不属于机构管理员用户
                        return Response(status=status.HTTP_403_FORBIDDEN)
                return Response(data, status=status.HTTP_200_OK)
            except Exception as e:
                set_run_info(level='error', address='/status_operation/view.py/get_org_name',
                             keyword='获取机构名称失败：{}'.format(e))
                return Response(status=status.HTTP_404_NOT_FOUND)

        else:
            # 用户账号不可用
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
def set_par_status(request):
    # 人员状态设置
    if request.method == 'POST':
        try:
            # print(request.data)
            param_dict = request.data
            uuid_list = param_dict.getlist('uuidlist', '')
            par_status = int(param_dict.get('status', 0))
            models.Participant.objects.filter(uuid__in=uuid_list).update(is_show=par_status)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/set_par_status',
                         keyword='修改人员状态失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
def set_user_status(request):
    """
    用户禁用或者开启，设置状态
    :param request:
    # :param uuid:
    :return:
    """
    user_id = request.POST.get('user_id')
    tag = int(request.POST.get('tag'))
    try:
        if tag == 1:
            models.User.objects.filter(id=user_id).update(is_active=True)
        else:
            models.User.objects.filter(id=user_id).update(is_active=False)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='禁用/开启用户({}):{}'.format(user_id, tag), user_obj=request.user)
        # -- 记录结束 --
        return Response(1)
    except Exception as e:
        set_run_info(level='error', address='/status_operation/view.py/set_user_status',
                     keyword='修改用户状态失败：{}'.format(e))
        return Response(0)


@api_view(['GET'])
def user_username_search(request):
    """
    新建用户-用户名是否存在验证
    :param request:
    :return:0:未找到重复，可以添加，1：有重复，不可添加
    """
    username = request.GET.get('username', '')
    tag = request.GET.get('tag', 'c')  # 区分是“创建:c”还是“修改:e”--修改的话，判断是不是本身，本身不算重复
    edit_user_id = request.GET.get('edit_user_id', '')  # 待修改的用户id
    # print(username)
    data = models.User.objects.filter(username=username)
    if tag == 'c':
        if data:
            return Response(1)
        else:
            return Response(0)
    else:
        if data:
            data_tmp = data.filter(id=edit_user_id)
            if data_tmp:
                # 是同一用户修改-原名
                return Response(0)
            else:
                return Response(1)
        else:
            return Response(0)


@api_view(['GET'])
def user_id_card_search(request):
    """
    新建用户-防止同一身份被用于同类型账号
    :param request:
    :return:1:已存在 0：不存在
    """
    # print(request.GET)
    id_card = request.GET.get('id_card', '')
    roles = int(request.GET.get('roles', ''))
    tag = request.GET.get('tag', 'c')  # 区分是“创建:c”还是“修改:e”--修改的话，判断是不是本身，本身不算重复
    edit_user_id = request.GET.get('edit_user_id', '')  # 待修改的用户id
    if roles in [settings.FIRST_LEVEL_MANAGER_GROUP, settings.GENERAL_ORG_GROUP]:
        # 机构用户
        data = models.User.objects.filter(id_card=id_card, org__id__isnull=False)
    else:
        data = models.User.objects.filter(id_card=id_card)
    if data:
        if tag == 'c':
            return Response(1)
        else:
            data_tmp = data.filter(id=edit_user_id)
            if data_tmp:
                # 是同一用户修改-原名
                return Response(0)
            else:
                return Response(1)
    else:
        return Response(0)


@api_view(['GET'])
def verify_org_manager_exist(request):
    """
    验证机构管理员是否存在
    :param request:
    :return:1:已存在 0：不存在  404:报错
    """
    org_id = request.query_params.get('org_id', -1)
    try:
        org_obj_list = models.Organization.objects.filter(id=org_id)
        if org_obj_list:
            org_obj = org_obj_list[0]
            # 验证机构和机构管理员是否存在
            user_obj = models.User.objects.filter(org=org_obj)
            user_id_list = [j.id for j in user_obj]
            group_id_obj = Group.objects.filter(user__in=user_id_list, id=settings.FIRST_LEVEL_MANAGER_GROUP)
            if group_id_obj:
                # 本机构管理员已存在
                return Response(1)
            else:
                return Response(0)
        else:
            return Response(0)

    except Exception as e:
        set_run_info(level='error', address='/status_operation/view.py/verify_org_manager_exist',
                     keyword='验证机构管理员是否存在：{}'.format(e))
        return Response(404)

# @api_view(['GET'])
# def get_daily_logins(request):
#     # 统计每日登录量
#     if request.method == 'GET':
#         try:
#             current_date = time.strftime('%Y-%m-%d')
#             data = UserBehavior.objects.values('user_id').filter(
#                 create_time__gte=current_date, user__isnull=False).distinct('user_id')
#             data_count = data.count()
#             return Response({"data": data, "count": data_count}, status=status.HTTP_200_OK)
#         except Exception as e:
#             set_run_info(level='error', address='/status_operation/view.py/get_daily_logins',
#                          keyword='统计每日登录量失败：{}'.format(e))
#             return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_user_org_groups(request):
    # 一个机构下多少用户
    if request.method == 'GET':
        try:
            data = models.User.objects.values('org__id', 'org__name').annotate(user_sum=Count('org')).filter(is_active=True, org__isnull=False)
            # print(data.query)
            for i in range(len(data)):
                user_obj = models.User.objects.values('username', 'first_name').filter(org=data[i]['org__id']).filter(is_active=True, org__isnull=False)
                data[i]['user_list'] = user_obj

            return Response({"data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/get_user_org_groups',
                         keyword='统计一个机构下多少用户：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
def get_user_to_par_status(request):
    """针对普通个人用户-获取研究人员认证审批状态 404：未申请 0:审批中 1：已通过 2：已驳回"""
    user = request.user
    if type(user) == AnonymousUser:
        set_run_info(level='error', address='/status_operation/view.py/get_is_par_ing',
                     keyword='获取研究人员认证审批状态失败：获取不到user')
        return Response({'result': 400}, status=status.HTTP_200_OK)

    obj_tmp = models.UserToParticipant.objects.values('up_status').filter(user=user.id)
    roles = user.groups.all().first()
    if obj_tmp:
        return Response({'result': obj_tmp[0]['up_status'], 'roles': roles.id}, status=status.HTTP_200_OK)
    else:
        return Response({"result": 404, 'roles': roles.id}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
def get_pending_approval_count(request):
    """
    获得待审批数量--超级管理员
    """
    user = request.user

    if type(user) == AnonymousUser:
        set_run_info(level='error', address='/status_operation/view.py/get_pending_approval_count',
                     keyword='获得待审批数量失败：获取不到user')
        return Response({'result': 400}, status=status.HTTP_200_OK)
    group_id_obj = Group.objects.filter(user=user.id)
    group_id_list = [i.id for i in group_id_obj]
    res = dict()
    if user.is_superuser or settings.SUPER_USER_GROUP in group_id_list or settings.PLANT_MANAGER_GROUP in group_id_list:
        res['register'] = models.UserRegister.objects.values('id').filter(info_status=0)
        res['topar'] = models.UserToParticipant.objects.values('id').filter(up_status=0)
        res['tovip'] = models.ParToVIP.objects.values('id').filter(result=0)
        return Response({'result': 200, 'res': res}, status=status.HTTP_200_OK)
    else:
        return Response({"result": 403}, status=status.HTTP_200_OK)
