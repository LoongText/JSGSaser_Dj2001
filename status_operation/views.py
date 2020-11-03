from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from tables.models import Projects, Research, ProRelations, UserDownloadBehavior
from tables.models import User, Bid, Organization, Participant
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
        user_id = request.query_params.get('userid', 0)
        ways = request.query_params.get('d', 'v')  # 区分查看还是下载
        try:
            obj = Projects.objects.filter(uuid=uuid)[0]
            if ways == 'd':
                obj.download_num_update()  # 下载量+1
                if user_id and user_id != 'undefined' and user_id != 'null':
                    user_obj = User.objects.get(id=user_id)
                    UserDownloadBehavior.objects.create(user=user_obj, pro=obj)  # 记录下载量数据
                else:
                    UserDownloadBehavior.objects.create(pro=obj)  # 记录下载量数据
            # 显示在弹出对话框中的默认的下载文件名
            the_file_name = '{}.pdf'.format(obj.name)
            # print(the_file_name)
            # download_url_fin = os.path.join(os.path.join(settings.BASE_DIR, 'static'), str(obj.attached))
            download_url_fin = os.path.join(settings.MEDIA_ROOT, str(obj.attached))
            # print(download_url_fin)
            # print(content_disposition)
            # 将汉字换成ascii码，否则下载名称不能正确显示
            the_file_name = urllib.parse.quote(the_file_name)
            response = StreamingHttpResponse(file_iterator(download_url_fin))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(the_file_name)

            return response

            # return Response(status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/projects_download',
                         user=user_id, keyword='成果下载失败：{}'.format(e))
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
            compare_status = Projects.objects.get(uuid=uuid).status
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
            data = Projects.objects.filter(uuid=uuid)
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
                par_pro_obj = ProRelations.objects.filter(pro=pro_obj_id)
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
                    par_pro_obj = ProRelations.objects.filter(pro=pro_obj_id)
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
            data = Research.objects.filter(uuid=uuid)
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
            param_dict = request.data
            id_list = param_dict.get('idlist', '')
            # print(id_list, type(id_list))
            bid_status = int(param_dict.get('status', 0))
            tag = param_dict.get('tag', 'sq')  # sq：批量处理申请  jt：批量处理结题
            data = Bid.objects.filter(id__in=id_list)
            if tag == 'sq':
                if bid_status in [0, 1, 2, 3, 4]:
                    data.update(bidder_status=bid_status)
            else:
                if bid_status in [0, 1, 2, 3]:
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
            Organization.objects.filter(uuid__in=uuid_list).update(is_show=org_status)
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
                    data = Organization.objects.values('id', 'name', 'competent_dpt')
                else:
                    user_org = user.org
                    if user_org:
                        org_list = [user_org.id]
                        for org_id in org_list:
                            subordinate_unit_obj = Organization.objects.values('id').filter(
                                superior_unit=org_id)
                            subordinate_unit_id = [i['id'] for i in subordinate_unit_obj]
                            org_list.extend(subordinate_unit_id)
                        data = Organization.objects.values('id', 'name', 'competent_dpt').filter(id__in=org_list)
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
            Participant.objects.filter(uuid__in=uuid_list).update(is_show=par_status)
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
            User.objects.filter(id=user_id).update(is_active=True)
        else:
            User.objects.filter(id=user_id).update(is_active=False)
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
    :return:
    """
    username = request.GET.get('username', '')
    # print(username)
    data = User.objects.filter(username=username)
    if data:
        return Response(1)
    else:
        return Response(0)


@api_view(['GET'])
def user_id_card_search(request):
    """
    新建用户-防止同一身份被用于同类型账号
    :param request:
    :return:
    """
    # print(request.GET)
    id_card = request.GET.get('id_card', '')
    roles = int(request.GET.get('roles', ''))
    if roles in [settings.FIRST_LEVEL_MANAGER_GROUP, settings.GENERAL_ORG_GROUP]:
        # 机构用户
        data = User.objects.filter(id_card=id_card, org__id__isnull=False)
    else:
        data = User.objects.filter(id_card=id_card)
    if data:
        return Response(1)
    else:
        return Response(0)


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
            data = User.objects.values('org__id', 'org__name').annotate(user_sum=Count('org')).filter(is_active=True, org__isnull=False)
            # print(data.query)
            for i in range(len(data)):
                user_obj = User.objects.values('username', 'first_name').filter(org=data[i]['org__id']).filter(is_active=True, org__isnull=False)
                data[i]['user_list'] = user_obj

            return Response({"data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/get_user_org_groups',
                         keyword='统计一个机构下多少用户：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)