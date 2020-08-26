import rest_framework
from django.contrib.auth import login, logout, authenticate
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from django.contrib.auth .models import Group
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from tables.models import User, RunInfo, UserBehavior
from rest_framework.decorators import authentication_classes
from login.auth import ExpiringTokenAuthentication
from django.views.decorators.csrf import csrf_exempt


class LoginView(viewsets.ViewSet):
    """
    登录验证
    """
    @csrf_exempt
    def create(self, request):
        param_dict = request.data
        username = param_dict.get('username', '').strip()
        password = param_dict.get('password', '').strip()
        print(param_dict)
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                group_id_obj = Group.objects.filter(user=user.id)
                # 属于多个组的，取最小id（权限最大）
                group_id_list = [i.id for i in group_id_obj]
                # print('---', user, type(user))
                user_org = user.org
                if user_org:
                    user_org = str(user_org)
                old_token = Token.objects.filter(user=user)
                old_token.delete()
                # 创建新的Token
                token = Token.objects.create(user=user)
                if user.first_name:
                    nickname = user.first_name
                else:
                    nickname = user.username
                roles = get_user_org_roles(user.id)
                res = {"status": 200, "username": user.username, "token": token.key, "userid": user.id,
                       "groupid_list": group_id_list, "user_org": user_org, "user_nickname": nickname, "roles": roles}
                # add_user_behavior(keyword='', search_con='用户登录', user_obj=user)
            else:
                res = {'status': 403}

            print(res)
            return Response(res)
        else:
            res = {'status': 403}
            print('用户名和密码不匹配')
            return Response(res)


class LoginOutView(viewsets.ViewSet):
    """
    退出登录状态
    """
    @staticmethod
    def list(request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


def requires_auth(f):
    """
    登录验证装饰器
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = None
        if len(args) > 0:
            for i in args:
                # print('--', type(i))
                if type(i) == rest_framework.request.Request:
                    # print(i.headers)
                    auth = i.user.is_authenticated
                    # print(i.user)
                    # print(auth)
        if not auth:
            return Response(status=status.HTTP_403_FORBIDDEN)
            # print('验证去')
        return f(*args, **kwargs)
    return decorated
 

@api_view(['POST'])
def do_something(request):
    """权限验证类，仅用于自测"""
    receive = request.data
    print(receive)
    if request.user.is_authenticated:   # 验证Token是否正确
        print("Do something...")
        return Response({"msg": "验证通过"})
    else:
        print("验证失败")
        return Response({"msg": "验证失败"})


@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
def set_passwd(request):
    """
    修改密码
    :param request:
    :return:
    """
    param_dict = request.data
    print(request.user)
    old_psd = param_dict.get('old_password', '')
    new_psd = param_dict.get('new_password', '')
    username = request.user.username
    user = authenticate(username=username, password=old_psd)
    try:
        # print('---', user)
        if user.is_active:
            user.set_password(new_psd)
            user.save()
            res = {"code": 201, "msg": "修改成功"}
        else:
            res = {"code": 403, "msg": "修改失败, 用户未激活"}
    except Exception as e:
        # print(e, type(e))
        RunInfo.objects.create(level='error', address='/login/view.py/set_passwd', user=user, keyword='修改密码失败：{}'.format(e))
        res = {"code": 403, "msg": "修改失败，{}".format(e)}
    return Response(res)


def get_user_org_roles(user_id):
    try:
        if user_id and user_id != 'undefined' and user_id != 'null':
            group_id_obj = Group.objects.filter(user=user_id)
            # 属于多个组的，取最小id（权限最大）
            group_id_list = [i.id for i in group_id_obj]
            if group_id_list:
                high_level = min(group_id_list)
                if high_level in [1, 2]:
                    roles = 'a'
                else:
                    is_a_dict = User.objects.values('org__is_a').get(id=user_id)
                    if is_a_dict['org__is_a']:
                        roles = 'a'
                    else:
                        roles = 'b'
            else:
                roles = 'b'
        else:
            roles = 'b'
        return roles
    except Exception as e:
        return 'b'


def set_run_info(level, address, keyword, user=None):
    """
    记录运行报错、警告信息
    :param level: 类型（警告、报错）
    :param address: 出错位置
    :param user: 用户
    :param keyword: 描述信息
    :return:
    """
    RunInfo.objects.create(level=level, address=address, user=user, keyword=keyword)


def add_user_behavior(keyword: str, search_con: str, user_obj=None):
    """
    添加行为记录
    :param keyword: 关键词, 不为空
    :param search_con: 内容，不为空
    :param user_obj: 对象，为空时是游客
    :return:
    """
    UserBehavior.objects.create(user=user_obj, keyword=keyword, search_con=search_con)