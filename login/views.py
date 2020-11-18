from django.contrib.auth import logout, authenticate
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import Group
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes
from login.auth import ExpiringTokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from login.LoginSerializer import UserRegisterListSerializer as urls
from login.LoginSerializer import UserRegisterCreateSerializer as urcs
from login.LoginSerializer import UserRegisterRetriveSerializer as urrs
from rest_framework.decorators import action
from query.split_page import SplitPages
from functools import wraps
import rest_framework
from jsg import settings
from tables import models
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.http import StreamingHttpResponse
import urllib.parse
import os


class LoginView(viewsets.ViewSet):
    """
    登录验证
    """

    @csrf_exempt
    def create(self, request):
        param_dict = request.data
        username = param_dict.get('username', '').strip()
        password = param_dict.get('password', '').strip()
        # print(param_dict)
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                group_id_obj = Group.objects.filter(user=user.id)
                group_id_list = [i.id for i in group_id_obj]
                # print('---', user, type(user))
                user_org = user.org
                if user_org:
                    user_org = str(user_org)
                # user_par = user.par
                # if user_par:
                #     user_par = user_par
                old_token = Token.objects.filter(user=user)
                old_token.delete()
                # 创建新的Token
                token = Token.objects.create(user=user)
                # print('---', token)
                if user.first_name:
                    nickname = user.first_name
                else:
                    nickname = user.username
                # roles = get_user_org_roles(user.id)
                res = {"status": 200, "username": user.username, "token": token.key, "userid": user.id,
                       "groupid_list": group_id_list, "user_org": user_org, "user_nickname": nickname}
                add_user_behavior(keyword='', search_con='用户登录', user_obj=user)
            else:
                res = {'status': 403}

            # print(res)
            return Response(res)
        else:
            res = {'status': 403}
            # print('用户名和密码不匹配')
            return Response(res)


class LoginOutView(viewsets.ViewSet):
    """
    退出登录状态
    """

    @staticmethod
    def list(request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class RegisterView(viewsets.GenericViewSet, mixins.CreateModelMixin,
                   mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """
    注册管理
    """
    queryset = models.UserRegister.objects.all()
    authentication_classes = (ExpiringTokenAuthentication,)

    def get_serializer_class(self):
        if self.action == "list":
            return urls
        elif self.action == 'create':
            return urcs
        elif self.action == 'retrieve':
            return urrs

    @action(methods=['get'], detail=False)
    # @super_manager_auth
    def get_register_user(self, request):
        """
        获得待审批的用户-注册来的,仅提供给平台管理员和超管
        :param request：
        :return:
        """
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        keyword = request.query_params.get('kw', '')
        roles = request.query_params.get('roles', 0)  # 2100：机构管理员 4200：个人用户  -- 筛选用
        info_status = request.query_params.get('info_status', 0)  # 状态筛选

        page = self.try_except(page, 1)  # 验证类型
        page_num = self.try_except(page_num, 10)  # 验证返回数量

        data = models.UserRegister.objects.values('id', 'name', 'roles', 'cell_phone', 'create_date', 'info_status'
                                                  ).filter(info_status=info_status)
        if keyword:
            data = data.filter(Q(username__contains=keyword) | Q(first_name__contains=keyword))
        if roles:
            data = data.filter(roles=roles)

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()
        for i in range(len(res['res'])):
            res['res'][i]['roles'] = settings.ROLES_DICT.get(res['res'][i]['roles'])
            res['res'][i]['info_status'] = settings.REGISTER_APPROVAL_RESULT.get(res['res'][i]['info_status'])
        return Response(res, status=status.HTTP_200_OK)

    @staticmethod
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            param_key = param_default
            set_run_info(level='error', address='/login/view.py/RegisterView',
                         keyword='强转参数出错{}'.format(e))
        return param_key

    @action(methods=['POST'], detail=True)
    def set_register_user(self, request, pk):
        """
        账号审批
        :param request:
        :return:
        """
        param_dict = request.data
        info_status = param_dict.get('status')  # 1：通过 2：否决  0：未处理
        remarks = param_dict.get('remarks')  # 备注
        try:
            user_tmp = models.UserRegister.objects.filter(id=pk)
            if int(info_status) == 1:
                # 同意创建账号
                if user_tmp:
                    user_obj = user_tmp[0]
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)

                new_user_obj = models.User.objects.create(
                    first_name=user_obj.name,
                    username=user_obj.username,
                    password=make_password(user_obj.login_pwd),
                    id_card=user_obj.id_card_code,
                    cell_phone=user_obj.cell_phone,
                    email=user_obj.email
                )
                if new_user_obj:
                    # 添加角色组
                    groups_list_obj = Group.objects.filter(id=user_obj.roles)
                    new_user_obj.groups.add(*groups_list_obj)

                if user_obj.roles == settings.FIRST_LEVEL_MANAGER_GROUP:
                    # 获取关联机构id
                    org_info = self.choose_or_create_org(user_obj)
                    org_id = org_info.get("org_id")
                    if org_id == '-1':
                        return Response(status=status.HTTP_404_NOT_FOUND)

                    new_user_obj.org = models.Organization.objects.get(id=org_id)
                    new_user_obj.save()

                user_tmp.update(info_status=1, remarks=remarks)
            else:
                # 驳回账号
                user_tmp.update(info_status=2, remarks=remarks)
            add_user_behavior(keyword='', search_con='账号审批({}:{})'.format(pk, info_status), user_obj=request.user)
        except Exception as e:
            set_run_info(level='error', address='/login/view.py/RegisterView-set_register_user',
                         keyword='注册账号审批失败：{}'.format(e))
        return Response(status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def get_verity_file(self, request, pk):
        """
        查看注册机构管理员证明材料
        :param request:
        :param pk:
        :return:
        """
        try:
            obj = models.UserRegister.objects.get(id=pk)
            the_file_name = '{}.pdf'.format(obj.username)
            download_url_fin = os.path.join(settings.MEDIA_ROOT, str(obj.certification_materials))
            # 将汉字换成ascii码，否则下载名称不能正确显示
            the_file_name = urllib.parse.quote(the_file_name)
            response = StreamingHttpResponse(self.file_iterator(download_url_fin))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(the_file_name)
            return response
        except Exception as e:
            set_run_info(level='error', address='/login/view.py/RegisterView-get_verity_file',
                         keyword='查看注册机构管理员证明材料失败：{}'.format(e))
            return Response({'msg': "查看注册机构管理员证明材料失败", "status": 404}, status=status.HTTP_200_OK)

    # 读取文件
    @staticmethod
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

    @staticmethod
    def choose_or_create_org(user_obj):
        """
        选择或者创建机构。并返回机构id
        :param user_obj: 注册用户对象
        :return:{"msg": 成功标志, "org_id": org对应id}
        """
        org_id_card_code = user_obj.id_card_code
        org_info = {"msg": 0, "org_id": -1}
        if org_id_card_code:
            org_obj = models.Organization.objects.filter(id_card_code=org_id_card_code)
            if org_obj:
                # 机构库里面有直接挂
                org_id = org_obj.first().id
            else:
                # 机构库里面没有啧创建
                org_obj_tmp = models.Organization.objects.create(id_card_code=org_id_card_code,
                                                                 name=user_obj.name)
                org_id = org_obj_tmp.id
            org_info["msg"] = 1
            org_info["org_id"] = org_id
        else:
            set_run_info(level='error', address='/login/view.py/RegisterView-set_register_user',
                         keyword='注册账号审批失败：{}'.format('注册信息中没有机构信用码'))
        return org_info


@api_view(['POST'])
def do_something(request):
    """权限验证类，仅用于自测"""
    receive = request.data
    # print(receive)
    if request.user.is_authenticated:  # 验证Token是否正确
        print("Do something...")
        return Response({"msg": "验证通过"})
    else:
        print("验证失败")
        return Response({"msg": "验证失败"})


@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
def set_password(request):
    """
    修改密码--当有user_id的时候，是重置密码功能,重置别人的密码
    只有激活状态下才能修改密码
    :param request:
    :return:
    """
    param_dict = request.data
    # print(param_dict)
    user_id = param_dict.get('userid', 0)
    old_psd = param_dict.get('old_password', '')
    new_psd = param_dict.get('new_password', '')
    # user = None
    try:
        if user_id:
            user = models.User.objects.get(pk=user_id)
        else:
            username = request.user.username
            user = authenticate(username=username, password=old_psd)

        user.set_password(new_psd)
        user.save()
        res = {"code": 201, "msg": "修改成功"}
    except Exception as e:
        # print(e, type(e))
        models.RunInfo.objects.create(level='error', address='/login/view.py/set_passwd',
                                      user=request.user, keyword='修改密码失败：{}'.format(e))
        res = {"code": 403, "msg": "修改失败，{}".format(e)}
    return Response(res)


def get_all_org_nature():
    org_level_obj = models.OrgNature.objects.values('id', 'remarks', 'level')
    org_level_list = [i['level'] for i in org_level_obj]
    org_level_list.remove(0)
    org_level_list_fin = list(set(org_level_list))
    # print(org_level_list_fin)
    return org_level_list_fin


def get_user_org_nature(user_id):
    org_level_list = get_all_org_nature()
    try:
        user_org_nature_level = settings.ORG_NATURE_LOWER_LEVEL
        if user_id and user_id != 'undefined' and user_id != 'null':
            user_org_nature_obj = models.User.objects.values('is_superuser', 'org__nature__level').get(id=user_id)
            # print(user_org_nature_obj)
            if user_org_nature_obj:
                if user_org_nature_obj['is_superuser']:
                    user_org_nature_level = settings.ORG_NATURE_HIGHER_LEVEL
                else:
                    user_org_nature_level = user_org_nature_obj['org__nature__level']
                # print('***', user_org_nature_level)
        org_nature_level_list = [j for j in org_level_list if j >= user_org_nature_level]
        # print('---', org_nature_level_list)
        return org_nature_level_list
    except Exception as e:
        # print('@@@', e)
        return [settings.ORG_NATURE_LOWER_LEVEL]


def set_run_info(level, address, keyword, user=None):
    """
    记录运行报错、警告信息
    :param level: 类型（警告、报错）
    :param address: 出错位置
    :param user: 用户
    :param keyword: 描述信息
    :return:
    """
    models.RunInfo.objects.create(level=level, address=address, user=user, keyword=keyword)


def add_user_behavior(keyword: str, search_con: str, user_obj=None):
    """
    添加行为记录
    :param keyword: 关键词, 不为空
    :param search_con: 内容，不为空
    :param user_obj: 对象，为空时是游客
    :return:
    """
    try:
        models.UserBehavior.objects.create(user=user_obj, keyword=keyword, search_con=search_con)
    except Exception as e:
        set_run_info(level='error', address='/login/view.py/add_user_behavior',
                     keyword='添加行为记录出错{}'.format(e))


def super_manager_auth(f):
    """
    验证是否是超管和平台管理员
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth = False
        if len(args) > 0:
            for i in args:
                # print('---', i, type(i))
                if type(i) == rest_framework.request.Request:
                    # print(i.headers)
                    user = i.user
                    if user.is_active:
                        group_id_obj = Group.objects.filter(user=user)
                        group_id_list = [i.id for i in group_id_obj]
                        if user.is_superuser or settings.SUPER_USER_GROUP in group_id_list or settings.PLANT_MANAGER_GROUP in group_id_list:
                            auth = True
        if not auth:
            return Response(status=status.HTTP_403_FORBIDDEN)
            # print('验证去')
        return f(*args, **kwargs)

    return decorated
