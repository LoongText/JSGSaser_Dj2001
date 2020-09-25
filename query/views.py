from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from tables.models import Projects, Research, Participant, ProRelations, Organization, UserClickBehavior, User
from tables.models import HotWords, Bid
from django.contrib.auth .models import Group
from django.db.models import Sum, Count, Q
import datetime
from login.auth import ExpiringTokenAuthentication
from query.split_page import SplitPages
from jsg import settings
from jsg.settings import ORG_NATURE_LOWER_LEVEL, ORG_NATURE_HIGHER_LEVEL
from jsg.settings import ORG_GROUP_LOWER_LEVEL, ORG_GROUP_MANAGER_LEVEL, ORG_GROUP_SUPERUSER_LEVEL
from login.views import add_user_behavior
from login.views import set_run_info
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import action
import os
import time
import json
from query.upload_file import UploadFile


def get_user_org_level(user_id):
    """
    获得用户的机构等级
    :return:
    """
    try:
        if user_id and user_id != 'undefined' and user_id != 'null':
            user_obj = User.objects.get(id=user_id)
            group_id_obj = Group.objects.filter(user=user_id)
            group_id_list = [i.id for i in group_id_obj]
            if group_id_list:
                org_group = min(group_id_list)
            else:
                org_group = ORG_GROUP_LOWER_LEVEL
            # 超管和管理员最高权限
            if org_group == ORG_GROUP_MANAGER_LEVEL or org_group == ORG_GROUP_SUPERUSER_LEVEL:
                org_level = ORG_NATURE_HIGHER_LEVEL
            else:
                if user_obj.org:
                    org_level = user_obj.org.nature.level
                else:
                    org_level = ORG_NATURE_LOWER_LEVEL
        else:
            org_level = ORG_NATURE_LOWER_LEVEL
        return org_level
    except Exception as e:
        # logger.error('get_user_org_level:{}'.format(e))
        set_run_info(level='error', address='/query/view.py/get_user_org_level',
                     user=user_id, keyword='获得用户机构等级失败：{}'.format(e))
        return ORG_NATURE_LOWER_LEVEL


# 分权限
def get_user_permission(user):
    """
    区分管理员与普通人员
    :param user: 登录对象
    :return: user_permission-查看等级，1：所有数据可操作 0：只能看自己的数据
    """
    # print(user, type(user))
    if user.is_active:
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
    else:
        return {"user_permission": 0, "org_id": 0}


def permission_filter_data(user_permission_dict, data, args, **kwargs):
    """
    权限过滤数据--目前只区分管理员和普通用户
    :param user_permission_dict: 权限和机构id字典{"user_permission": 0, "org_id": 0}
    :param data: 数据对象
    :param args: 过滤条件1
    :param kwargs: 过滤条件2
    :return:
    """
    if user_permission_dict['user_permission']:
        # 是管理员
        data = data.filter(**kwargs)
    else:
        # 普通用户
        data = data.filter(**{args: user_permission_dict['org_id']})
    # print('---', data.query)
    return data


class ProjectsQueryView(viewsets.ViewSet):
    """
    成果搜索
    """
    def list(self, request):
        # 成果分类（1：发展，2：监管，3：党建，4：改革，5：其他，100：全部）
        print(request.query_params)
        cls_t = request.query_params.get('cls', 100)
        # 查询列
        column = request.query_params.get('column', 'name')
        # 搜索关键字
        keyword = request.query_params.get('kw', '')
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 30)
        s_date = request.query_params.get('start_date', '2000-01-01')
        e_date = request.query_params.get('end_date', datetime.date.today())
        # 排序方式
        order = request.query_params.get('order', 't')
        # 登录用户id
        user_id = request.query_params.get('userid', 0)
        # 机构id, 按机构搜索成果的时候
        org_id = request.query_params.get('org_id', 0)
        # 人员id, 按人员搜索成果的时候
        par_id = request.query_params.get('par_id', 0)

        cls_t = self.try_except(cls_t, 100)  # 验证分类
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 30)  # 验证每页的数量
        org_id = self.try_except(org_id, 0)  # 验证机构id
        par_id = self.try_except(par_id, 0)  # 验证人员id

        data = Projects.objects.values('id', 'uuid', 'name', 'key_word', 'release_date', 'views').filter(status=1)

        if keyword:
            data = self.filter_keyword(data, keyword, column, user_id)

        if cls_t != 100:
            data = data.filter(classify=cls_t)

        data = self.filter_date(data, s_date, e_date)

        org_obj = ''
        par_obj = ''
        if org_id and not par_id:
            # 指定机构查询
            data = self.designated_org_inquiry(data, org_id)
            # 机构研究人员姓名
            par_obj = Participant.objects.values('id', 'name').filter(unit__id=org_id, is_show=True)

        elif par_id and not org_id:
            # 指定人员查询
            data = self.designated_par_inquiry(data, par_id)

        else:
            # 根据成果按机构统计数量
            org_obj = data.values('research', 'research__name').annotate(pro_sum=Count('id', distinct=True)).filter(
                research__isnull=False).order_by('-pro_sum')[:5]

        # 按分类统计数量
        cls_dict = [{"classify": cls_t, "cls_num": data.count()}]
        if cls_t == 100:
            cls_dict = data.values('classify').annotate(cls_num=Count('classify'))

        if order == 't':
            # 按时间倒序排列
            data = data.order_by('-release_date', '-id')
            # data = data.order_by('-release_time')
        elif order == 'v':
            # 按浏览量倒序排列
            data = data.order_by('-views')
        elif order == 'd':
            # 按下载量倒序排列
            data = data.order_by('-downloads')

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        org_level_list = [3, 4]
        org_level = get_user_org_level(user_id)
        # print('query_', org_level)
        if org_level == 1:
            org_level_list = [1, 2, 3, 4]

        for i in range(len(res['res'])):
            res['res'][i]['research'] = self.get_search_str(res['res'][i]['id'], org_level_list)

        res['org'] = org_obj
        res['cls'] = cls_dict
        res['par'] = par_obj

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
            set_run_info(level='error', address='/query/view.py/ProjectsQueryView-list',
                         keyword='强转参数出错：{}'.format(e))
            # logger.info('query --view.py --try_except --强转参数出错{}，--赋默认值'.format(e))
        return param_key

    @staticmethod
    def get_lead_org_str(pro_id: int):
        # 获得多对多字段牵头机构名称
        lead_org = Projects.objects.get(pk=pro_id).lead_org.all()
        # print(lead_org)
        org_list = ''
        if lead_org:
            org_list = [i.name for i in lead_org]
        org_str = ''
        if org_list:
            org_str = ';'.join(org_list)
        return org_str

    @staticmethod
    def get_search_str(pro_id: int, org_level_list: list):
        # 获得多对多字段研究机构名称
        org_list = []
        research_org = Projects.objects.get(pk=pro_id).research.all()
        # print(research_org)
        if research_org:
            # 判断添加研究机构
            for r_org in research_org:
                if r_org.nature.level in org_level_list:
                    org_list.append(r_org.name)
        org_str = ''
        if org_list:
            org_str = ';'.join(org_list)
        return org_str

    @staticmethod
    def filter_date(data, s_date, e_date):
        """
        日期过滤
        :param data:
        :param s_date: 起始日期
        :param e_date: 结束日期
        :return:
        """
        if s_date and s_date != 'NaN-NaN-NaN' and s_date != 'null':
            # 判断日期
            if e_date and e_date != 'NaN-NaN-NaN' and e_date != 'null':
                data = data.filter(release_date__gte=s_date, release_date__lte=e_date)
            else:
                data = data.filter(release_date__gte=s_date)
        else:
            if e_date and e_date != 'NaN-NaN-NaN' and e_date != 'null':
                data = data.filter(release_date__lte=e_date)
        return data

    @staticmethod
    def filter_keyword(data, keyword, column, user_id):
        """
        关键词过滤
        :param data:
        :param keyword: 关键词
        :param column: 查询列
        :param user_id: 用户id
        :return:
        """
        keyword = str(keyword).replace(' ', '')
        column_kd = '{}__contains'.format(column)
        data = data.filter(**{column_kd: keyword})

        # 添加行为记录
        try:
            if user_id and user_id != 'undefined' and user_id != 'null':
                user_obj = User.objects.filter(pk=user_id)
            else:
                user_obj = None
            if user_obj:
                # -- 记录开始 --
                add_user_behavior(
                    keyword=keyword,
                    search_con='查询成果信息({})'.format(str(data.query)),
                    user_obj=user_obj[0])
                # -- 记录结束 --
            else:
                add_user_behavior(keyword=keyword, search_con='查询成果信息({})'.format(str(data.query)))
        except Exception as e:
            add_user_behavior(keyword=keyword, search_con='查询成果信息({})'.format(str(data.query)))
            set_run_info(level='error', address='/query/view.py/ProjectsQueryView-list',
                         user=user_id, keyword='搜索成果-添加行为记录失败：{}'.format(e))

        return data

    @staticmethod
    def designated_org_inquiry(data, org_id):
        """
        指定机构查询
        :param data:
        :param org_id: 机构id
        :return:
        """
        lead_org_data = data.filter(lead_org__id=org_id)
        re_org_data = data.filter(research__id=org_id)
        lead_org_data_list = []
        re_org_data_list = []
        if lead_org_data:
            lead_org_data_list = [i['id'] for i in lead_org_data]
        if re_org_data:
            re_org_data_list = [i['id'] for i in re_org_data]
        all_org_list_set = set(lead_org_data_list + re_org_data_list)
        data = data.filter(id__in=all_org_list_set)

        return data

    @staticmethod
    def designated_par_inquiry(data, par_id):
        """
        指定人员查询
        :param data:
        :param par_id: 人员id
        :return:
        """
        relation_data = ProRelations.objects.values('pro').filter(is_eft=1, par=par_id).distinct('pro')
        pro_id_list = [i['pro'] for i in relation_data]
        data = data.filter(id__in=pro_id_list)
        return data


class MyProjectsQueryView(viewsets.ViewSet):
    """
    我的成果信息--查询列表和修改
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    def list(self, request):
        # print(request.query_params)
        # 分类（1：发展，2：监管，3：党建，4：改革，5：其他，100：全部）
        cls_t = request.query_params.get('cls', 100)
        keyword = request.query_params.get('kw', '')  # 搜索关键字
        pro_status = request.query_params.get('status', 0)
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 30)

        cls_t = self.try_except(cls_t, 100)  # 验证分类
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 30)  # 验证每页的数量

        # status=5 删除状态 0:不显示
        data = Projects.objects.values('uuid', 'name', 'classify__cls_name', 'key_word', 'user__first_name',
                                       'status').exclude(status__in=[0, 5]).order_by('-id')
        if keyword:
            data = data.filter(Q(name__contains=keyword) | Q(key_word__contains=keyword))
            # -- 记录开始 --

            add_user_behavior(keyword=keyword, search_con='搜索成果信息：{}'.format(str(data.query)),
                              user_obj=request.user)

            # -- 记录结束 --

        if cls_t != 100:
            data = data.filter(classify=cls_t)

        if pro_status:
            data = data.filter(status=pro_status)

        # -- 权限开始 --
        user = request.user
        user_permission_dict = get_user_permission(user)
        data = permission_filter_data(user_permission_dict, data, 'user__org', status=1)
        # -- 权限结束 --

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        for i in range(len(res['res'])):
            if res['res'][i]['status'] in [0, 2, 3, 4]:
                res['res'][i]['edit'] = 1
            else:
                res['res'][i]['edit'] = 0

            res['res'][i]['status'] = settings.PROJECTS_STATUS_CHOICE[res['res'][i]['status']]

        return Response(res, status=status.HTTP_200_OK)

    def post(self, request):
        """
        成果修改
        :param request:
        :return:
        """
        param_dict = request.data
        print('---', param_dict)
        pro_status = param_dict.get('pro_status', 0)
        name = param_dict.get('name')
        uuid = param_dict.get('uuid')
        bid = param_dict.get('bid_id')
        lead_org_id_list_str = param_dict.get('lead_org_id_list')
        research_id_list_str = param_dict.get('research_id_list')
        classify = param_dict.get('classify')
        key_word = param_dict.get('key_word')
        release_date = param_dict.get('release_date')
        attached = request.FILES.get('attached')
        par_obj_list_str = param_dict.get('par_obj_list')

        pro_obj = Projects.objects.filter(uuid=uuid)

        current_year = datetime.datetime.now().year
        current_month = '{:02d}'.format(datetime.datetime.now().month)
        current_date = time.strftime('%Y-%m-%d')

        # 成果上传保存路径
        pro_save_path_dirs = os.path.join(
            os.path.join(os.path.join(settings.MEDIA_ROOT, 'attached'), str(current_year)),
            current_month)

        # 若用户不选择发布时间，自动填充发布时间
        if pro_status == 3:
            if release_date == 'Null' or release_date is None:
                release_date = current_date
        else:
            if release_date == 'Null' or release_date is None:
                release_date = None

        try:
            # 设置关系表
            par_obj_list = json.loads(par_obj_list_str)
            if par_obj_list:
                self.set_pro_relations(pro_obj, par_obj_list)

            # 设置研究机构和立项机构
            lead_org_id_list = json.loads(lead_org_id_list_str)
            research_id_list = json.loads(research_id_list_str)
            self.set_many_to_many_org(pro_obj, lead_org_id_list, research_id_list)

            # print('attached_path', attached, type(attached))
            if attached:
                file_obj = UploadFile(pro_save_path_dirs, attached)
                attached_name_fin = file_obj.handle()

                pro_obj.update(
                    name=name,
                    classify=classify,
                    key_word=key_word,
                    status=pro_status,
                    release_date=release_date,
                    bid=bid,
                    attached="attached/{}/{}/{}".format(current_year, current_month, attached_name_fin)
                )
            else:
                pro_obj.update(
                    name=name,
                    classify=classify,
                    key_word=key_word,
                    status=pro_status,
                    bid=bid,
                    release_date=release_date,
                )
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='修改成果信息：{};{}'.format(str(request.data), str(attached)),
                              user_obj=request.user)
            # -- 记录结束 --
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            # print(e)
            set_run_info(level='error', address='/backstage/view.py/project_edit_do',
                         user=request.user.id, keyword='修改成果失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def set_pro_relations(pro_obj, par_obj_list):
        """
        填写关系表， 三表对应
        :param pro_obj: 成果对象
        :param par_obj_list: 人员对象列表
        :return:
        """
        for par_dict in par_obj_list:
            # print(par_dict, type(par_dict))
            roles = int(par_dict['roles'])
            par_id = int(par_dict['id'])
            job = par_dict['job']
            pro_relation_obj = ProRelations.objects.filter(pro=pro_obj[0].id, par=par_id)
            score = settings.ROLES_SCORE[roles]
            if pro_relation_obj:
                pro_relation_obj.update(job=job, roles=roles, score=score)
            else:
                par_obj = Participant.objects.get(id=par_id)
                ProRelations.objects.create(is_eft=False, par=par_obj, org=par_obj.unit, pro=pro_obj[0],
                                            job=job, roles=roles, score=score)

    @staticmethod
    def set_many_to_many_org(pro_obj, lead_org_id_list, research_id_list):
        """
        设置研究机构和立项机构
        :param pro_obj: 成果对象
        :param lead_org_id_list: 立项机构列表
        :param research_id_list: 研究机构列表
        :return:
        """
        # 多对多对象删除
        pro_obj[0].lead_org.clear()
        pro_obj[0].research.clear()

        # 多对多对象创建
        if lead_org_id_list:
            # lead_org_id_list = lead_org_id_str.split(';')
            print('&&&', lead_org_id_list, type(lead_org_id_list))
            lead_org_id_list_obj = Organization.objects.filter(id__in=lead_org_id_list)
            # print(lead_org_id_list_obj)
            pro_obj[0].lead_org.add(*lead_org_id_list_obj)

        if research_id_list:
            # research_id_list = research_id_str.split(';')
            print(research_id_list)
            research_id_list_obj = Organization.objects.filter(id__in=research_id_list)
            pro_obj[0].research.add(*research_id_list_obj)

    @staticmethod
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            param_key = param_default
            set_run_info(level='error', address='/query/view.py/MyProjectsQueryView',
                         keyword='强转参数出错{}'.format(e))
        return param_key


class SPProjectsQueryView(viewsets.ViewSet):
    """
    审批成果信息以及历史
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    def list(self, request):
        # 分类（1：发展，2：监管，3：党建，4：改革，5：其他，100：全部）
        cls_t = request.query_params.get('cls', 100)
        keyword = request.query_params.get('kw', '')  # 搜索关键字
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 30)
        tag = request.query_params.get('tag', 'td')  # td:待审批 his:历史

        cls_t = self.try_except(cls_t, 100)  # 验证分类
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 30)  # 验证每页的数量

        # status=5 删除状态
        if tag == 'td':
            data = Projects.objects.values('id', 'uuid', 'name', 'classify__cls_name', 'status',
                                           'attached', 'user__first_name').filter(status=3).order_by('-id')
        else:
            data = Projects.objects.values('id', 'uuid', 'name', 'classify__cls_name', 'status', 'user__first_name',
                                           ).filter(status__in=[1, 4]).order_by('-id')
        if keyword:
            data = data.filter(Q(name__contains=keyword) | Q(lead_org__name__contains=keyword) |
                               Q(research__name__contains=keyword))
            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='审批成果信息以及历史{}'.format(tag), user_obj=request.user)
            # -- 记录结束 --

        if cls_t != 100:
            data = data.filter(classify=cls_t)

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        for i in range(len(res['res'])):
            res['res'][i]['status'] = settings.PROJECTS_STATUS_CHOICE[res['res'][i]['status']]
            res['res'][i]['lead_org'] = self.get_lead_org_str(res['res'][i]['id'])
            res['res'][i]['research'] = self.get_search_str(res['res'][i]['id'])

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
            set_run_info(level='error', address='/query/view.py/MyProjectsQueryView',
                         keyword='强转参数出错{}'.format(e))
        return param_key

    @staticmethod
    def get_lead_org_str(pro_id: int):
        # 获得多对多字段牵头机构名称
        lead_org = Projects.objects.get(pk=pro_id).lead_org.all()
        # print(lead_org)
        org_list = ''
        if lead_org:
            org_list = [i.name for i in lead_org]
        org_str = ''
        if org_list:
            org_str = ';'.join(org_list)
        return org_str

    @staticmethod
    def get_search_str(pro_id: int):
        # 获得多对多字段研究机构名称
        org_list = []
        research_org = Projects.objects.get(pk=pro_id).research.all()
        # print(research_org)
        if research_org:
            org_list = [i.name for i in research_org]
        org_str = ''
        if org_list:
            org_str = ';'.join(org_list)
        return org_str


class ProDetailView(viewsets.ViewSet):
    """
    成果详情页
    """
    # authentication_classes = (ExpiringTokenAuthentication,)

    def list(self, request):
        uuid = request.query_params.get('uuid', '')
        user_id = request.query_params.get('userid', '')
        tag = request.query_params.get('tag', 'web')  # 前端看：web，后端看：back
        # print('-----', user_id)
        # user = request.user

        user_obj = self.get_user_obj(user_id)  # 获取用户对象
        if tag == 'web':
            org_level = get_user_org_level(user_id)  # 获取机构等级
        else:
            org_level = ORG_NATURE_HIGHER_LEVEL

        try:
            obj_list = Projects.objects.filter(uuid=uuid)
            if obj_list:
                obj = obj_list[0]
            else:
                res = {'res': '没有找到记录'}
                return Response(res, status=status.HTTP_404_NOT_FOUND)
            # print(obj)
            lead_org_obj = obj.lead_org.all()
            research_org_obj = obj.research.all()

            par_id_obj = ProRelations.objects.values(
                'par__name', 'roles', 'speciality', 'job', 'task', 'org__name', 'par__id').filter(
                pro=obj.id, par__id__isnull=False).order_by('roles')

            if org_level == ORG_NATURE_HIGHER_LEVEL:
                lead_org_dict = self.filter_show_org(lead_org_obj, [])
                research_org_dict = self.filter_show_org(research_org_obj, [])
                UserClickBehavior.objects.create(user=user_obj, pro=obj)  # 创建点击记录
            else:
                par_id_obj = par_id_obj.filter(org__nature__level__in=[4])
                lead_org_dict = self.filter_show_org(lead_org_obj, [1, 2, 3])
                research_org_dict = self.filter_show_org(research_org_obj, [1, 2, 3])
                UserClickBehavior.objects.create(pro=obj)  # 创建点击记录

            cls_t = ''
            if obj.classify:
                cls_t = obj.classify.cls_id

            obj.views_num_update()  # 浏览量+1

            obj_dict = {"lead_org": lead_org_dict, "research": research_org_dict, "key_word": obj.key_word,
                        "release_date": obj.release_date, "abstract": obj.abstract,
                        "attached": str(obj.attached), "classify": cls_t,
                        "reference": str(obj.reference).split(';'), "par": par_id_obj, 'name': obj.name
                        }
            # print(obj_dict)
            if tag == 'back':
                bid_re_title = obj.bid
                submitter_org = obj.user
                if bid_re_title:
                    bid_re_title = bid_re_title.re_title
                if submitter_org:
                    submitter_org = submitter_org.first_name
                back_append_dict = {'status': settings.PROJECTS_STATUS_CHOICE[obj.status],
                                    'bid_re_title': bid_re_title,
                                    'downloads': obj.downloads, 'views': obj.views,
                                    'submitter_org': submitter_org
                                    }
                # 与前段一致，将人员的par__id值命名为id
                for i in range(len(par_id_obj)):
                    # print(par_id_obj[i])
                    par_id_obj[i]['id'] = par_id_obj[i]['par__id']
                back_append_dict['par'] = par_id_obj
                obj_dict.update(back_append_dict)

            res = {'res': obj_dict}

            add_user_behavior(keyword='', search_con='查看成果详情({})'.format(uuid), user_obj=user_obj)

            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/ProDetailView-list',
                         keyword='成果详情-获得成果详细信息失败：{}'.format(e), user=user_id)
            # logger.info('detail --view.py --{}'.format(e))
            res = {'res': '没有找到记录'}
            return Response(res, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_user_obj(user_id):
        """
        获得user对象
        :user_id:用户id
        :return:
        """
        try:
            if user_id and user_id != 'undefined' and user_id != 'null':
                user = User.objects.get(id=user_id)
                if user.is_active:
                    user_obj = user
                else:
                    user_obj = None
            else:
                user_obj = None
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/ProDetailView-list',
                         keyword='成果详情-获取用户出错：{}'.format(e), user=user_id)
            user_obj = None

        return user_obj

    @staticmethod
    def filter_show_org(org_obj, level_list: list):
        """
        过滤要展示的研究机构和立项机构
        :org_obj:带过滤的机构
        :level_list:可以展示的机构等级
        :return:
        """
        org_dict = {}
        if org_obj:
            if level_list:
                for l_org in org_obj:
                    if l_org.nature.level not in [1, 2, 3]:
                        org_dict[l_org.id] = l_org.name
            else:
                for l_org in org_obj:
                    org_dict[l_org.id] = l_org.name
        # org_str = ';'.join(org_list)
        return org_dict


class ResearchQueryView(viewsets.ViewSet):
    """
    课题搜索（招标搜索）
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    def list(self, request):
        keyword = request.query_params.get('kw', '')
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 8)
        column = request.query_params.get('column', 'name')
        tag = request.query_params.get('tag', 'all')  # 区分公共查看(all)还是个人后台查看(personal)
        # print(request.query_params)
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 8)  # 验证每页数量

        data = Research.objects.values('id', 'uuid', 'name', 'classify__cls_name', 'start_date', 'end_date',
                                       'guidelines', 'user__org__name', 'contacts', 'phone', 'status', 'funds'
                                       ).filter(status__in=[0, 1, 2, 3])

        if keyword:
            keyword = str(keyword).replace(' ', '')
            # cls_t不作为检索条件
            if column not in ['name', 'contacts', 'user__first_name']:
                column = 'name'
            cond = {'{}__contains'.format(column): keyword}
            data = data.filter(**cond)
            # print('1', data.query)

        if tag == 'all':
            # 前方页面显示未发布中状态的招标
            data = data.filter(status=1).order_by('-start_date')
        elif tag == 'personal':
            # -- 权限开始 --
            user = request.user
            user_permission_dict = get_user_permission(user)
            data = permission_filter_data(user_permission_dict, data, 'user__org', status__in=[1, 2, 3])

            # -- 权限结束 --
            # 排序
            data = data.order_by('-id')

            for i in range(len(data)):
                if data[i]['status'] == 0:
                    data[i]['edit'] = 1
                else:
                    data[i]['edit'] = 0
                # 统计投标数量
                bid_count = Bid.objects.filter(bidder_status=1, bidding=data[i]['id']).count()
                data[i]['bid_count'] = bid_count
                # 统计已审批投标数量
                bid_ed_count = Bid.objects.filter(bidder_status__in=[2, 3], bidding=data[i]['id']).count()
                data[i]['bid_ed_count'] = bid_ed_count
                # 统计申请结题数量
                bid_conclusion = Bid.objects.filter(conclusion_status=1, bidding=data[i]['id']).count()
                data[i]['bid_conclusion'] = bid_conclusion
                # 统计已审批申请结题数量
                bid_ed_conclusion = Bid.objects.filter(conclusion_status__in=[2, 3], bidding=data[i]['id']).count()
                data[i]['bid_ed_conclusion'] = bid_ed_conclusion
                # 将状态改为对应含义
                data[i]['status'] = settings.RESEARCH_STATUS_CHOICE[data[i]['status']]

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

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
            set_run_info(level='error', address='/query/view.py/ResearchQueryView-list',
                         keyword='强转参数出错：{}'.format(e))
        return param_key


class ResearchDetailView(viewsets.ViewSet):
    """
    课题详情（招标详情）
    """

    @staticmethod
    def list(request):
        uuid = request.query_params.get('uuid', '')
        if uuid:
            try:
                data = Research.objects.values('id', 'uuid', 'name', 'classify', 'start_date', 'end_date', 'guidelines',
                                               'funds', 'brief', 'contacts', 'phone', 'user__org__name').get(uuid=uuid)
                # print(data)
                res = {'res': data}
                return Response(res, status=status.HTTP_200_OK)
            except Exception as e:
                set_run_info(level='error', address='/query/view.py/ResearchDetailView-list',
                             keyword='获取课题详情失败：{}'.format(e))
                # logger.info('re_detail --view.py --{}'.format(e))
                res = {'res': '没有找到记录'}
                return Response(res, status=status.HTTP_404_NOT_FOUND)
        else:
            set_run_info(level='error', address='/query/view.py/ResearchDetailView-list',
                         keyword='获取课题详情-参数uuid缺失')
            # logger.info('re_detail --view.py --缺失uuid')
            res = {'res': '缺失参数'}
            return Response(res, status=status.HTTP_404_NOT_FOUND)

    # def post(self, request):
    #     # 修改
    #     param_dict = request.data
    #     uuid = param_dict.get('uuid', '')
    #     name = param_dict.get('name', '')
    #     classify = param_dict.get('classify', 5)
    #     start_date = param_dict.get('start_date', '')
    #     end_date = param_dict.get('end_date', '')
    #     guidelines = param_dict.get('guidelines', '')
    #     re_status = param_dict.get('status', 0)
    #     funds = param_dict.get('funds', 0)
    #     contacts = param_dict.get('contacts', '')
    #     phone = param_dict.get('phone', '')
    #     brief = param_dict.get('brief', '')
    #     # print('guuuuu', param_dict)
    #     re_obj = Research.objects.filter(uuid=uuid)
    #     current_year = datetime.datetime.now().year
    #     current_month = '{:02d}'.format(datetime.datetime.now().month)
    #     # current_time = time.strftime('%H%M%S')
    #     # 课题上传保存路径
    #     re_save_path_dirs = os.path.join(
    #         os.path.join(os.path.join(settings.MEDIA_ROOT, 'guide'), str(current_year)),
    #         current_month)
    #
    #     if re_obj:
    #         try:
    #             if guidelines:
    #                 file_obj = UploadFile(re_save_path_dirs, guidelines)
    #                 attached_name_fin = file_obj.handle()
    #                 # 重新上传文件操作  setting/MEDIA.ROOT
    #                 # 判断目录是否存在,不存在就创建
    #                 # self.create_dirs_not_exist(re_save_path_dirs)
    #                 # 保存的路径
    #                 # save_path = os.path.join(re_save_path_dirs, guidelines.name)
    #                 # 判断文件是否存在, 避免重名
    #                 # save_path, attached_name_fin = self.file_name_is_exits(re_save_path_dirs, guidelines, current_time)
    #                 # print('save_path', save_path)
    #                 # 在保存路径下，建立文件
    #                 # with open(save_path, 'wb') as f:
    #                 #     在f.chunks()上循环保证大文件不会大量使用你的系统内存
    #                 #     for content in guidelines.chunks():
    #                 #         f.write(content)
    #
    #                 re_obj.update(name=name, classify=classify, start_date=start_date, funds=funds, contacts=contacts,
    #                               end_date=end_date, phone=phone, brief=brief, status=re_status,
    #                               guidelines="guide/{}/{}/{}".format(current_year, current_month, attached_name_fin))
    #             else:
    #                 re_obj.update(name=name, classify=classify, start_date=start_date, funds=funds, contacts=contacts,
    #                               end_date=end_date, phone=phone, brief=brief, status=re_status)
    #             return Response(1, status=status.HTTP_200_OK)
    #         except Exception as e:
    #             set_run_info(level='error', address='/query/view.py/ResearchDetailView-post',
    #                          keyword='修改课题详情失败：{}'.format(e))
    #             return Response(0, status=status.HTTP_200_OK)
    #     else:
    #         set_run_info(level='error', address='/query/view.py/ResearchDetailView-post',
    #                      keyword='修改课题详情失败：未获取到记录')
    #         return Response(0, status=status.HTTP_200_OK)


class SPBidHistoryView(viewsets.ViewSet):
    """
    审批投标/投标结题信息（未审批+已审批）
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    def list(self, request):
        # 搜索关键字
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 1)
        keyword = request.query_params.get('kd', '')
        param = request.query_params.get('param', 'bid')  # bid：审批  jt：结题
        tag = request.query_params.get('tag', 'td')  # td:未审批  ed:已审批
        re_id = request.query_params.get('re_id')

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 8)  # 验证每页数量

        data = Bid.objects.values('id', 're_title', 'bidder_date', 'bidder_status', 'bidder', 'leader', 'lea_phone',
                                  'contacts', 'con_phone', 'bidding__name', 'conclusion_status').filter(bidding=re_id)
        if keyword:
            data = data.filter(
                Q(re_title__contains=keyword) | Q(bidder_date__contains=keyword) | Q(
                    bidding__name__contains=keyword))
        if tag == 'td':
            # 未审批
            status_list = [1]
        else:
            status_list = [2, 3]
        if param == 'bid':
            data = data.filter(bidder_status__in=status_list)
        else:
            data = data.filter(conclusion_status__in=status_list)
        # -- 记录开始 --
        add_user_behavior(keyword=keyword, search_con='查看招标结题审批记录{}'.format(param), user_obj=request.user)
        # -- 记录结束 --

        data = data.order_by('-id')
        sp = SplitPages(data, page, page_num)
        res = sp.split_page()
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
            set_run_info(level='error', address='/query/view.py/BidQueryView-list',
                         keyword='强转参数出错{}'.format(e))
            # logger.info('query_d --view.py --try_except --强转参数出错{}，--赋默认值'.format(e))
        return param_key


class MyBidQueryView(viewsets.ViewSet):
    """
    我的投标信息
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        keyword = request.query_params.get('kd', '')
        tag = request.query_params.get('tag', 'vue')  # vue:前端  back：后台列表
        bid_status = request.query_params.get('status', 100)  # 100代表未输入
        user = request.user

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 30)  # 验证每页的数量
        bid_status = self.try_except(bid_status, 100)  # 验证状态

        if tag == 'vue':
            # 上传课题做关联用
            if user.is_active:
                data = Bid.objects.values('id', 're_title').filter(submitter=user.id, bidder_status=2).order_by('-id')
            else:
                data = ''
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = Bid.objects.values(
                'id', 'bidding__name', 're_title', 'bidder_date', 'bidder_status',
                'funds', 'contacts', 'con_phone', 'conclusion_status').exclude(bidder_status=4).order_by('-id')

            if keyword:
                data = data.filter(Q(bidding__name__contains=keyword) | Q(re_title__contains=keyword) |
                                   Q(bidder_date__contains=keyword) | Q(funds__contains=keyword) |
                                   Q(contacts__contains=keyword) | Q(con_phone__contains=keyword))

                # -- 记录开始 --
                add_user_behavior(keyword=keyword, search_con='搜索投标信息', user_obj=user)
                # -- 记录结束 --

            if bid_status != 100:
                data = data.filter(bidder_status=bid_status)

            # -- 权限开始 --
            # user = request.user
            user_permission_dict = get_user_permission(user)
            data = permission_filter_data(user_permission_dict, data, 'submitter__org', bidder_status__in=[1, 2, 3])
            # -- 权限结束 --

            # print(data.count())
            sp = SplitPages(data, page, page_num)
            res = sp.split_page()
            for i in range(len(res['res'])):
                res['res'][i]['bidder_status'] = settings.BIDDER_STATUS_CHOICE[res['res'][i]['bidder_status']]
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
            set_run_info(level='error', address='/query/view.py/MyBidQueryView-list',
                         keyword='强转参数出错{}'.format(e))
        return param_key


class BidQueryView(viewsets.ViewSet):
    """
    投标信息
    """
    def list(self, request):
        # 分类（1：发展，2：监管，3：党建，4：改革，5：其他，100：全部）
        # 搜索关键字
        keyword = request.query_params.get('keyword', '')
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 8)
        column = request.query_params.get('column', 're_title')
        tag = request.query_params.get('tag', 'doing')  # 课题推进doing还是课题结题done
        # print(request.query_params)
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 8)  # 验证每页数量
        data = Bid.objects.values('id', 're_title', 'bidder', 'bidding__classify__cls_name',
                                  'bidder_date__year', 'leader', 'bidder_status', 'conclusion_status').order_by('-id')

        if tag == 'doing':
            data = data.filter(bidder_status__in=[1, 2], conclusion_status=0)
        elif tag == 'done':
            data = data.filter(conclusion_status__in=[1, 2])

        if keyword:
            keyword = str(keyword).replace(' ', '')
            # cls_t不作为检索条件
            if column not in ['re_title', 'bidder', 'leader']:
                column = 're_title'
            cond = {'{}__contains'.format(column): keyword}
            data = data.filter(**cond)
            # print('1', data.query)

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        # 获取每个课题参与的人数
        for i in range(len(res['res'])):
            pro_id_obj = Projects.objects.values('id').filter(bid=res['res'][i]['id'], status=1)
            if pro_id_obj:
                pro_id_list = [i['id'] for i in pro_id_obj]
                par_sum = ProRelations.objects.values('par').filter(pro__in=pro_id_list).distinct().count()
            else:
                par_sum = 0
            res['res'][i]['par_sum'] = par_sum

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
            set_run_info(level='error', address='/query/view.py/BidQueryView-list',
                         keyword='强转参数出错{}'.format(e))
            # logger.info('query_d --view.py --try_except --强转参数出错{}，--赋默认值'.format(e))
        return param_key


class ParticipantsQueryView(viewsets.ViewSet):
    """
    研究人员搜索
    """

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 8)
        name = request.query_params.get('name', '')
        par_id = request.query_params.get('par_id', '')

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 8)  # 验证每页的数量
        # par_id = self.try_except(par_id, 0)  # 验证人员id

        if par_id:
            data = Participant.objects.values('id', 'name', 'unit', 'brief', 'job', 'pro_sum', 'photo'
                                              ).filter(pk=par_id, is_show=True)
        else:
            data = Participant.objects.values('id', 'name', 'unit', 'pro_sum').filter(is_show=True).order_by('id')
            if name:
                data = data.filter(name__contains=name)

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        for i in range(len(res['res'])):
            if res['res'][i]['unit']:
                res['res'][i]['unit'] = Organization.objects.get(pk=res['res'][i]['unit']).name
            # 个人总评分
            res['res'][i]['score_num'] = \
                ProRelations.objects.filter(par_id=res['res'][i]['id'], is_eft=True).aggregate(Sum('score'))[
                    'score__sum']
            speciality_list = ProRelations.objects.values('speciality').filter(par_id=res['res'][i]['id'])
            speciality = ''
            for i_dict in speciality_list:
                if i_dict['speciality']:
                    speciality += '{};'.format(i_dict['speciality'])
            # 专业特长
            res['res'][i]['speciality'] = speciality
            pro_id_list = ProRelations.objects.values('pro_id').filter(par_id=res['res'][i]['id'], is_eft=True)
            pro_id_list_fin = [i_dict['pro_id'] for i_dict in pro_id_list]
            # 成果总浏览量
            res['res'][i]['view_sum'] = \
                Projects.objects.filter(id__in=pro_id_list_fin, status=1).aggregate(Sum('views'))[
                    'views__sum']
            # 成果总下载量
            res['res'][i]['download_sum'] = \
                Projects.objects.filter(id__in=pro_id_list_fin, status=1).aggregate(Sum('downloads'))[
                    'downloads__sum']
        return Response(res, status=status.HTTP_200_OK)

    @staticmethod
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            # logger.info('researcher --view.py --try_except --强转参数出错{}，--赋默认值'.format(e))
            set_run_info(level='error', address='/query/view.py/PaticipantsQueryView-list',
                         keyword='强转参数出错{}'.format(e))
            param_key = param_default
        # print(param_key)
        return param_key


class MyParView(viewsets.ViewSet):
    """
    后台-专家检索
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        keyword = request.query_params.get('kw', '')

        page = self.try_except(page, 1)  # 验证类型
        page_num = self.try_except(page_num, 10)  # 验证返回数量

        data = Participant.objects.values('id', 'uuid', 'name', 'unit__name', 'job', 'email'
                                          ).exclude(is_show=0).order_by('-id')

        # -- 权限开始 --
        user = request.user
        user_permission_dict = get_user_permission(user)
        data = permission_filter_data(user_permission_dict, data, 'unit')
        # -- 权限结束 --

        if keyword:
            data = data.filter(Q(name__contains=keyword) | Q(unit__name__contains=keyword) |
                               Q(job__contains=keyword) | Q(email__contains=keyword))

            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='后台-搜索人员信息', user_obj=request.user)
            # -- 记录结束 --

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()
        return Response(res, status=status.HTTP_200_OK)

    @staticmethod
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/MyParView-list',
                         keyword='强转参数出错{}'.format(e))
            param_key = param_default
        return param_key


class OrgQueryView(viewsets.ViewSet):
    """
    研究机构搜索
    研究机构搜索、牵头机构搜索、机构推荐
    """

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 8)
        unit = request.query_params.get('unit', '')
        org_id = request.query_params.get('org_id', 0)
        a_b = request.query_params.get('roles', 'b')

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 8)  # 验证每页的数量
        org_id = self.try_except(org_id, 0)  # 验证id

        if org_id:
            data = Organization.objects.values('id', 'name', 'brief', 'pro_sum', 'par_sum', 'photo'
                                               ).filter(pk=org_id, is_show=True)
        else:
            data = Organization.objects.values('id', 'name', 'pro_sum', 'par_sum').filter(is_show=True).order_by('id')
            if a_b == 'a':
                data = data.filter(is_a=True)
            else:
                data = data.filter(is_b=True)
            if unit:
                data = data.filter(name__contains=unit)
        # print(data.query)
        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        for i in range(len(res['res'])):
            # 机构总评分
            score_sum = \
                ProRelations.objects.filter(org_id=res['res'][i]['id'], is_eft=True).aggregate(Sum('score'))[
                    'score__sum']
            if score_sum:
                res['res'][i]['score_sum'] = '%.2f' % score_sum
            else:
                res['res'][i]['score_sum'] = 0
            # 成果总浏览量
            res['res'][i]['view_sum'] = Projects.objects.filter(status=1).filter(
                Q(lead_org__id=res['res'][i]['id']) | Q(research__id=res['res'][i]['id'])).aggregate(Sum('views'))[
                'views__sum']
            # 成果总下载量
            res['res'][i]['download_sum'] = Projects.objects.filter(status=1).filter(
                Q(lead_org__id=res['res'][i]['id']) | Q(research__id=res['res'][i]['id'])).aggregate(Sum('downloads'))[
                'downloads__sum']
            # print(a)
        return Response(res, status=status.HTTP_200_OK)

    @staticmethod
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/OrgQueryView-list',
                         keyword='强转参数出错{}'.format(e))
            # logger.info('org --view.py --try_except --强转参数出错{}，--赋默认值'.format(e))
            param_key = param_default
        # print(param_key)
        return param_key


class MyOrgView(viewsets.ViewSet):
    """
    后台-机构检索
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    def list(self, request):
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        keyword = request.query_params.get('kw', '')

        page = self.try_except(page, 1)  # 验证类型
        page_num = self.try_except(page_num, 10)  # 验证返回数量

        data = Organization.objects.values('id', 'uuid', 'name', 'is_a', 'is_b', 'nature__remarks').filter(
            is_show=True).order_by('-id')

        # -- 权限开始 --
        user = request.user
        user_permission_dict = get_user_permission(user)
        data = permission_filter_data(user_permission_dict, data, 'id')
        # -- 权限结束 --

        if keyword:
            data = data.filter(Q(name__contains=keyword) | Q(nature__remarks__contains=keyword))

            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='后台-搜索机构信息', user_obj=request.user)
            # -- 记录结束 --

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()
        return Response(res, status=status.HTTP_200_OK)

    @staticmethod
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/MyOrgView-list',
                         keyword='强转参数出错{}'.format(e))
            param_key = param_default
        return param_key


class MyUserView(viewsets.ViewSet):
    """
    后台-用户检索
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    @action(methods=['get'], detail=False)
    def get_user_list(self, request):
        """
        用户列表搜索
        :param request:
        :return:
        """
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        keyword = request.query_params.get('kw', '')

        page = self.try_except(page, 1)  # 验证类型
        page_num = self.try_except(page_num, 10)  # 验证返回数量

        data = User.objects.values('id', 'username', 'first_name', 'is_active').order_by('-id')

        # -- 权限开始 --
        user = request.user
        user_permission_dict = get_user_permission(user)
        data = permission_filter_data(user_permission_dict, data, 'org')
        # -- 权限结束 --
        # if user_permission_dict['user_permission']:
        #     is_manage = 1
        # else:
        #     is_manage = 0

        if keyword:
            data = data.filter(Q(username__contains=keyword) | Q(first_name__contains=keyword))

            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='搜索用户信息', user_obj=request.user)
            # -- 记录结束 --

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()
        # res['is_manage'] = is_manage
        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def get_user_detail(self, request, pk):
        """
        用户详情
        :param request:
        :param pk: 用户id
        :return:
        """
        data = User.objects.filter(id=pk)
        if data:
            user_permission_dict = get_user_permission(data[0])
            data_fin = data.values('username', 'first_name', 'org', 'date_joined', 'last_login', 'is_active')[0]
            if user_permission_dict['user_permission']:
                data_fin['is_manage'] = 1
            else:
                data_fin['is_manage'] = 0
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='查看用户信息详情({})'.format(pk),
                              user_obj=request.user)
            # -- 记录结束 --
            return Response(data_fin, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def create(request):
        """
        创建用户
        :param request:
        :return:
        """
        param_dict = request.data
        username = param_dict.get('username')
        first_name = param_dict.get('first_name')
        password = param_dict.get('password')
        org_id = param_dict.get('org_id')
        org_name = param_dict.get('org')
        is_manage = int(param_dict.get('is_manage'), 0)
        groups_list = []
        print(param_dict)
        if is_manage:
            # 添加管理员组
            groups_list.append(2)

        if not first_name:
            # 如果没有昵称，则默认显示机构名称
            first_name = org_name

        org_name = org_name.replace(' ', '')
        org_obj_list = Organization.objects.filter(id=org_id, name=org_name)
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
            return Response(status=status.HTTP_404_NOT_FOUND)

        password_end = make_password(password, None, 'pbkdf2_sha256')  # 源字符串，固定字符串，加密方式
        try:
            User.objects.create(
                first_name=first_name,
                username=username,
                password=password_end,
                org=org_obj,
            )
            # 添加组
            user_obj = User.objects.get(username=username)
            groups_list_obj = Group.objects.filter(id__in=groups_list)
            user_obj.groups.add(*groups_list_obj)

            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='新增用户信息({})'.format(user_obj.id), user_obj=request.user)
            # -- 记录结束 --

            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            # 创建失败
            set_run_info(level='error', address='/query/view.py/MyUserView-create',
                         user=request.user.id, keyword='新增用户信息失败：{}'.format(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def put(request):
        """
        用户信息修改
        :param request:
        :return:
        """
        param_dict = request.data
        user_id = param_dict.get('user_id')
        first_name = param_dict.get('first_name')
        is_active = param_dict.get('is_active')
        org_id = param_dict.get('org_id')
        org_name = param_dict.get('org')
        is_manage = int(param_dict.get('is_manage'))
        print(param_dict)
        if is_manage:
            print(1)
            User.objects.get(id=user_id).groups.add(2)
        else:
            print(2)
            User.objects.get(id=user_id).groups.remove(2)

        try:
            org_name = org_name.replace(' ', '')
            org_obj_list = Organization.objects.filter(id=org_id, name=org_name)
            if not org_obj_list:
                # 机构不存在
                return Response(status=status.HTTP_404_NOT_FOUND)

            User.objects.filter(id=user_id).update(
                first_name=first_name,
                is_active=is_active,
                org=org_id
            )
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='编辑用户信息({}):{}'.format(user_id, str(param_dict)),
                              user_obj=request.user)
            # -- 记录结束 --
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            set_run_info(level='error', address='/query/view.py/MyUserView-update',
                         user=request.user.id, keyword='编辑用户信息失败：{}'.format(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/MyUserView-list',
                         keyword='强转参数出错{}'.format(e))
            param_key = param_default
        return param_key


class HotWordsView(viewsets.ViewSet):
    """
    热词推荐
    """

    @staticmethod
    def list(request):
        num = request.query_params.get('num', 10)
        try:
            num = int(num)
            if num < 1:
                num = 10
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/HotWordsView-list',
                         keyword='强转参数出错{}'.format(e))
            # logger.info('hot_word --view.py --try_except --强转参数出错{}，--赋默认值'.format(e))
            num = 10
        latest_date = list(HotWords.objects.values('create_date').order_by('-create_date')[:1])[0]['create_date']
        param = HotWords.objects.values('hot_word').filter(is_true=True, create_date=latest_date).order_by('num')[:num]
        res = {'res': param}
        return Response(res, status=status.HTTP_200_OK)
