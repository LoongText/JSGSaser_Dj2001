from django.contrib.auth import login, logout, authenticate
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth .models import Group
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes
from login.auth import ExpiringTokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from jsg import settings
from tables import models
from login.LoginSerializer import UserRegisterListSerializer as urls
from login.LoginSerializer import UserRegisterCreateSerializer as urcs
from functools import wraps
import rest_framework


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
                # add_user_behavior(keyword='', search_con='用户登录', user_obj=user)
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


class RegisterView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
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

# def requires_auth(f):
#     """
#     登录验证装饰器
#     """
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth = None
#         if len(args) > 0:
#             for i in args:
#                 # print('--', type(i))
#                 if type(i) == rest_framework.request.Request:
#                     # print(i.headers)
#                     auth = i.user.is_authenticated
#                     # print(i.user)
#                     # print(auth)
#         if not auth:
#             return Response(status=status.HTTP_403_FORBIDDEN)
#             # print('验证去')
#         return f(*args, **kwargs)
#     return decorated


@api_view(['POST'])
def do_something(request):
    """权限验证类，仅用于自测"""
    receive = request.data
    # print(receive)
    if request.user.is_authenticated:   # 验证Token是否正确
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