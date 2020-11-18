from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from tables import models
from django.contrib.auth .models import Group, AnonymousUser
from django.db.models import Sum, Count, Q
from login.auth import ExpiringTokenAuthentication
from query.split_page import SplitPages
from jsg import settings
from login.views import add_user_behavior
from login.views import set_run_info
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import action
from query.upload_file import UploadFile
from query.export_data import write2excel
from django.http import StreamingHttpResponse
import urllib.parse
# from login.views import super_manager_auth
from query import QuerySerializer
from uploads import UploadsSerializer
import os
import time
import json
import datetime


def get_user_group(user):
    group_id_obj = Group.objects.filter(user=user.id)
    group_id_list = [i.id for i in group_id_obj]
    return group_id_list


def permission_filter_data(user, data, args, **kwargs):
    """
    权限过滤数据
    :param user: 用户对象
    :param data: 数据对象
    :param args: 过滤条件1
    :param kwargs: 过滤条件2
    :return:
    """
    print(kwargs)
    if user.is_active:
        try:
            group_id_obj = Group.objects.filter(user=user.id)
            group_id_list = [i.id for i in group_id_obj]
            if user.org:
                org_id = user.org.id
            else:
                org_id = -1
            # print('--------', group_id_list)
            if user.is_superuser or settings.SUPER_USER_GROUP in group_id_list or settings.PLANT_MANAGER_GROUP in group_id_list:
                # 超管
                # data = data.filter(**kwargs)
                # print('超级管理员')
                pass
            elif settings.FIRST_LEVEL_MANAGER_GROUP in group_id_list:
                # 一级管理员
                # print('机构管理员')
                org_id_list = [org_id]
                if org_id_list:
                    for i in org_id_list:
                        org_id_list_tmp = models.Organization.objects.values('id').filter(superior_unit=i, is_show=True)
                        org_id_list_tmp_list = [j['id'] for j in org_id_list_tmp]
                        if org_id_list_tmp_list:
                            org_id_list.extend(org_id_list_tmp_list)
                # print('------', org_id_list)
                param = '{}__in'.format(args)
                data = data.filter(**{param: org_id_list})
            elif settings.GENERAL_ORG_GROUP in group_id_list:
                # 普通机构用户
                # 可见全部、仅可管理自己
                # print('普通机构用户')
                org_id_list = [org_id]
                if org_id_list:
                    for i in org_id_list:
                        org_id_list_tmp = models.Organization.objects.values('id').filter(superior_unit=i, is_show=True)
                        # print('11', org_id_list_tmp)
                        org_id_list_tmp_list = [j['id'] for j in org_id_list_tmp]
                        if org_id_list_tmp_list:
                            org_id_list.extend(org_id_list_tmp_list)
                # print('------', org_id_list)
                param = '{}__in'.format(args)
                data = data.filter(**{param: org_id_list})
                # param = '{}__in'.format(args)
                # data = data.filter(**{param: org_id})
            else:
                # 专家个人账号和普通个人账号
                # 无机构管理项-人员、用户仅可管理自己
                # print('普通个人用户')
                if kwargs.get('module') == 'user_manage':
                    data = data.filter(id=user.id)
                elif kwargs.get('module') == 'par_manage':
                    data = data.filter(id=user.par)
                else:
                    param = args.split('_')[0]
                    data = data.filter(**{param: user.id})
            # print('---', data.query)
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/permission_filter_data',
                         user=user.id, keyword='权限过滤：{}'.format(e))
    else:
        data = None
    return data


class ExportExcel(viewsets.ViewSet):
    """
    数据导出--指定导出
    """
    @staticmethod
    def list(request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        """
        指定数据导出
        :param request:
        :return:
        """
        # print(request.data)
        uuid_list = request.data.get('uuid', '')
        user_id = request.data.get('userid', '')
        n = len(uuid_list)
        # print(uuid_list, n, type(uuid_list))
        res_obj = self.get_pro_info(uuid_list, user_id)
        records = [[a['name'], a['lead_org'], a['research'], a['key_word'], a['release_date'], a['views'], a['downloads']] for a in res_obj]
        head_data = ['成果名称', '委托单位名称', '研究单位名称', '关键词', '发表时间', '本库浏览量', '本库下载量']
        # download_url = r'C:\Users\XIAO\Desktop\sjdc'
        download_url = os.path.join(settings.MEDIA_ROOT, 'tmp')
        download_url_fin = write2excel(n, head_data, records, download_url)
        the_file_name = 'sjdc.xls'
        # print(the_file_name, download_url_fin)
        # 将汉字换成ascii码，否则下载名称不能正确显示
        the_file_name = urllib.parse.quote(the_file_name)
        response = StreamingHttpResponse(self.file_iterator(download_url_fin))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(the_file_name)

        return response

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

    def get_pro_info(self, uuid_list: list, user_id):
        """
        获得需要导出的成果信息
        :param uuid_list: 需要导出的uuid列表
        :param user_id: 用户ID
        :return:
        """
        pro_data = models.Projects.objects.values(
            'id', 'name', 'key_word', 'release_date', 'views', 'downloads').filter(uuid__in=uuid_list)
        # org_level_list = [4]
        # org_level = get_user_org_level(user_id)
        # if org_level == 1:
        #     org_level_list = [1, 2, 3, 4]

        for i in range(len(pro_data)):
            lead_org_obj = models.Projects.objects.get(pk=pro_data[i]['id']).lead_org.all()
            # print('---', lead_org_obj)
            research_org_obj = models.Projects.objects.get(pk=pro_data[i]['id']).research.all()
            pro_data[i]['research'] = self.filter_show_org(research_org_obj)
            pro_data[i]['lead_org'] = self.filter_show_org(lead_org_obj)

        # print(pro_data)
        return pro_data

    @staticmethod
    def filter_show_org(org_obj):
        """
        过滤要展示的研究机构和立项机构
        :org_obj:带过滤的机构
        :return:
        """
        org_list = []
        if org_obj:
            for l_org in org_obj:
                org_list.append(l_org.name)
        org_str = ';'.join(org_list)
        return org_str
    # @staticmethod
    # def filter_show_org(org_obj, level_list: list):
    #     """
    #     过滤要展示的研究机构和立项机构
    #     :org_obj:带过滤的机构
    #     :level_list:可以展示的机构等级
    #     :return:
    #     """
    #     org_list = []
    #     if org_obj:
    #         for l_org in org_obj:
    #             if l_org.nature.level in level_list:
    #                 org_list.append(l_org.name)
    #
    #     org_str = ';'.join(org_list)
    #     return org_str


class ProjectsQueryView(viewsets.ViewSet):
    """
    成果搜索
    """
    def list(self, request):
        # print(request.query_params)
        cls_t = request.query_params.get('cls', 100)  # 成果分类（100：全部）
        column = request.query_params.get('column', 'name')  # 查询列name/text_part/key_word/research__name
        keyword = request.query_params.get('kw', '')  # 搜索关键字
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 30)
        s_date = request.query_params.get('start_date', '2000-01-01')
        e_date = request.query_params.get('end_date', datetime.date.today())
        order = request.query_params.get('order', 't')  # 排序方式
        user_id = request.query_params.get('userid', 0)  # 登录用户id
        org_id = request.query_params.get('org_id', 0)  # 机构id, 按机构搜索成果的时候
        par_id = request.query_params.get('par_id', 0)  # 人员id, 按人员搜索成果的时候

        cls_t = self.try_except(cls_t, 100)  # 验证分类
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 30)  # 验证每页的数量
        org_id = self.try_except(org_id, 0)  # 验证机构id
        par_id = self.try_except(par_id, 0)  # 验证人员id

        data = models.Projects.objects.values(
            'id', 'uuid', 'name', 'key_word', 'release_date', 'views', 'downloads', 'org_str', 'pro_source'
        ).filter(status=1)

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
            par_obj = models.Participant.objects.values('id', 'name').filter(unit__id=org_id, is_show=True)

        elif par_id and not org_id:
            # 指定人员查询
            data = self.designated_par_inquiry(data, par_id)

        else:
            # 根据成果按机构统计数量
            data = data.values('id', 'uuid', 'name', 'key_word', 'release_date',
                               'views', 'downloads', 'org_str', 'pro_source', 'abstract')
            # org_obj = data.values('research', 'research__name').annotate(pro_sum=Count('id', distinct=True)).filter(
            #     research__isnull=False).order_by('-pro_sum')[:5]

        # 按分类统计数量
        cls_dict = [{"classify": cls_t, "cls_num": data.count()}]
        if cls_t == 100:
            cls_dict = data.values('classify').annotate(cls_num=Count('classify'))

        if order == 't':
            # 按时间倒序排列
            data = data.order_by('-release_date', '-id')
        elif order == 'v':
            # 按浏览量倒序排列
            data = data.order_by('-views')
        elif order == 'd':
            # 按下载量倒序排列
            data = data.order_by('-downloads')

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        res['org'] = org_obj
        res['cls'] = cls_dict
        res['par'] = par_obj

        for i in range(len(res['res'])):
            research_obj = models.Projects.objects.get(id=res['res'][i]['id']).research.all()
            res['res'][i]['research'] = self.filter_show_org(research_obj)

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
        return param_key

    @staticmethod
    def filter_show_org(org_obj):
        """
        组合要展示的研究机构和立项机构
        :org_obj:机构
        :return:
        """
        org_list = []
        if org_obj:
            for l_org in org_obj:
                org_list.append({'id': l_org.id, 'name': l_org.name})
        return org_list

    def filter_date(self, data, s_date, e_date):
        """
        日期过滤
        :param data:
        :param s_date: 起始日期
        :param e_date: 结束日期
        :return:
        """

        if self.is_valid_date(s_date):
            # 判断日期
            if self.is_valid_date(e_date):
                data = data.filter(release_date__gte=s_date, release_date__lte=e_date)
            else:
                data = data.filter(release_date__gte=s_date)
        else:
            if self.is_valid_date(e_date):
                data = data.filter(release_date__lte=e_date)
        return data

    @staticmethod
    def is_valid_date(str_date):
        """判断是否是一个有效的日期字符串"""
        try:
            if str_date:
                time.strptime(str_date, "%Y-%m-%d")
                return 1
            else:
                return 0
        except Exception as e:
            print(e)
            # set_run_info(level='warn', address='/query/view.py/ProjectsQueryView-list',
            #              keyword='时间参数格式错误{}'.format(e))
            return 0

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
                user_obj = models.User.objects.filter(pk=user_id)
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
        relation_data = models.ProRelations.objects.values('pro').filter(is_eft=1, par=par_id).distinct('pro')
        pro_id_list = [i['pro'] for i in relation_data]
        data = data.filter(id__in=pro_id_list)
        return data


class ProjectsManageView(viewsets.ViewSet):
    """
    我的成果信息--查询列表、详情和修改
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    @action(methods=['get'], detail=False)
    def get_pro_list(self, request):
        # print(request.query_params)
        # 分类（1：发展，2：监管，3：党建，4：改革，5：其他，100：全部）
        cls_t = request.query_params.get('cls', 100)
        keyword = request.query_params.get('kw', '')  # 搜索关键字
        pro_status = request.query_params.get('status', -1)  # 默认返回全部
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 30)
        org = request.query_params.get('org_id', 0)  # 所属机构筛选

        cls_t = self.try_except(cls_t, 100)  # 验证分类
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 30)  # 验证每页的数量

        # status=5 删除状态 0:不显示
        data = models.Projects.objects.values('id', 'uuid', 'name', 'classify__cls_name', 'key_word', 'user',
                                              'user__org', 'user__org__name', 'status', 'downloads',
                                              'release_date', 'views'
                                              ).exclude(status__in=[0, 5]).order_by('-id')
        if keyword:
            data = data.filter(Q(name__contains=keyword) | Q(key_word__contains=keyword))
            # -- 记录开始 --

            add_user_behavior(keyword=keyword, search_con='搜索成果信息：{}'.format(str(data.query)),
                              user_obj=request.user)

            # -- 记录结束 --

        if cls_t != 100:
            # 类型筛选
            data = data.filter(classify=cls_t)

        if pro_status in [1, 2, 3, 4]:
            # 状态筛选
            data = data.filter(status=pro_status)

        if org:
            # 所属机构筛选
            data = data.filter(user__org=org)

        # -- 权限开始 --
        user = request.user
        data = permission_filter_data(user, data, 'user__org', status=1)
        if not data:
            return Response(status=status.HTTP_200_OK)
        # -- 权限结束 --

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        group_id_list = get_user_group(user)
        user_id = user.id if type(user) != AnonymousUser else 0

        for i in range(len(res['res'])):
            if res['res'][i]['status'] in [0, 2, 3, 4]:
                res['res'][i]['edit'] = 1
            else:
                res['res'][i]['edit'] = 0
            res['res'][i]['status'] = settings.PROJECTS_STATUS_CHOICE[res['res'][i]['status']]
            if settings.GENERAL_ORG_GROUP in group_id_list:
                # 对普通机构人员的限制（能看全部，仅能编辑自己）
                if res['res'][i]['user'] == user_id:
                    res['res'][i]['can_be_edit'] = 1
                else:
                    res['res'][i]['can_be_edit'] = 0
            else:
                res['res'][i]['can_be_edit'] = 1

        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_pro_detail(self, request):
        uuid = request.query_params.get('uuid', '')
        tag = request.query_params.get('tag', 'web')  # 前端看：web，后端看：back
        user_obj = request.user
        if type(user_obj) is AnonymousUser:
            user_obj = None
        # print('-----', user_obj, type(user_obj))
        try:
            obj_list = models.Projects.objects.filter(uuid=uuid)
            if obj_list:
                obj = obj_list[0]
                models.UserClickBehavior.objects.create(user=user_obj, pro=obj)  # 创建点击记录
            else:
                res = {'res': '没有找到记录'}
                return Response(res, status=status.HTTP_404_NOT_FOUND)
            # print(obj)
            lead_org_obj = obj.lead_org.all()
            lead_org_list = self.filter_show_org(lead_org_obj)
            if obj.pro_source == 'iser':
                research_org_obj = obj.research.all()
                research_org_list = self.filter_show_org(research_org_obj)
            else:
                research_org_list = obj.org_str

            par_id_obj = models.ProRelations.objects.values(
                'par__name', 'roles', 'speciality', 'job', 'task', 'org__name', 'par__id').filter(
                pro=obj.id, par__id__isnull=False).order_by('roles')

            cls_t = ''
            if obj.classify:
                cls_t = obj.classify.cls_id

            obj.views_num_update()  # 浏览量+1

            obj_dict = {"lead_org": lead_org_list, "research": research_org_list, "key_word": obj.key_word,
                        "release_date": obj.release_date, "abstract": obj.abstract, "pro_source": obj.pro_source,
                        "attached": str(obj.attached), "classify": cls_t, "uuid": obj.uuid,
                        "reference": str(obj.reference).split(';'), "par": par_id_obj, 'name': obj.name
                        }
            # print(obj_dict)
            if tag == 'back':
                bid_re_title = obj.bid
                submitter_org = obj.user
                if bid_re_title:
                    bid_re_title = bid_re_title.re_title
                submitter_org_name = ''
                if submitter_org:
                    submitter_org_name = submitter_org.org.name if submitter_org.org else ''
                back_append_dict = {'status': settings.PROJECTS_STATUS_CHOICE[obj.status],
                                    'bid_re_title': bid_re_title,
                                    'downloads': obj.downloads, 'views': obj.views,
                                    'submitter_org': submitter_org_name
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
                         keyword='成果详情-获得成果详细信息失败：{}'.format(e), user=user_obj.id)
            res = {'res': '没有找到记录'}
            return Response(res, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=False)
    def set_pro_detail(self, request):
        """
        成果修改
        :param request:
        :return:
        """
        param_dict = request.data
        # print('---', param_dict)
        pro_status = param_dict.get('pro_status', 0)
        name = param_dict.get('name')
        uuid = param_dict.get('uuid')
        bid = param_dict.get('bid_id')
        lead_org_id_list_str = param_dict.get('lead_org_id_list')
        research_id_list_str = param_dict.get('research_id_list')
        classify = param_dict.get('classify')
        key_word = param_dict.get('key_word')
        release_date = param_dict.get('release_date')
        abstract = param_dict.get('abstract')
        attached = request.FILES.get('attached')
        par_obj_list_str = param_dict.get('par_obj_list')

        pro_obj = models.Projects.objects.filter(uuid=uuid)

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
                    abstract=abstract,
                    attached="attached/{}/{}/{}".format(current_year, current_month, attached_name_fin)
                )
            else:
                pro_obj.update(
                    name=name,
                    classify=classify,
                    key_word=key_word,
                    status=pro_status,
                    bid=bid,
                    abstract=abstract,
                    release_date=release_date,
                )
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='修改成果信息：{};{}'.format(str(request.data), str(attached)),
                              user_obj=request.user)
            # -- 记录结束 --
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            # print(e)
            set_run_info(level='error', address='/query/view.py/project_edit_do',
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
            pro_relation_obj = models.ProRelations.objects.filter(pro=pro_obj[0].id, par=par_id)
            score = settings.ROLES_SCORE[roles]
            if pro_relation_obj:
                pro_relation_obj.update(job=job, roles=roles, score=score)
            else:
                par_obj = models.Participant.objects.get(id=par_id)
                models.ProRelations.objects.create(is_eft=False, par=par_obj, org=par_obj.unit, pro=pro_obj[0],
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
            # print('&&&', lead_org_id_list, type(lead_org_id_list))
            lead_org_id_list_obj = models.Organization.objects.filter(id__in=lead_org_id_list)
            # print(lead_org_id_list_obj)
            pro_obj[0].lead_org.add(*lead_org_id_list_obj)

        if research_id_list:
            # print(research_id_list)
            research_id_list_obj = models.Organization.objects.filter(id__in=research_id_list)
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

    @staticmethod
    def filter_show_org(org_obj):
        """
        组合要展示的研究机构和立项机构
        :org_obj:机构
        :return:
        """
        org_list = []
        if org_obj:
            for l_org in org_obj:
                org_list.append({'id': l_org.id, 'name': l_org.name})
        return org_list


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
            data = models.Projects.objects.values('id', 'uuid', 'name', 'classify__cls_name', 'status',
                                                  'attached', 'user__first_name').filter(status=3).order_by('-id')
        else:
            data = models.Projects.objects.values('id', 'uuid', 'name', 'classify__cls_name',
                                                  'status', 'user__first_name'
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
        lead_org = models.Projects.objects.get(pk=pro_id).lead_org.all()
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
        research_org = models.Projects.objects.get(pk=pro_id).research.all()
        # print(research_org)
        if research_org:
            org_list = [i.name for i in research_org]
        org_str = ''
        if org_list:
            org_str = ';'.join(org_list)
        return org_str


class GoodProjectsManageView(viewsets.ViewSet):
    """
    优秀成果管理
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    @action(methods=['get'], detail=False)
    def get_good_pro(self, request):
        """
        获取优秀成果列表（按照标记取值）
        :param request:
        :return:
        """
        keyword = request.query_params.get('kw', '')  # 搜索关键字
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 30)
        mark_id = request.query_params.get('mark_id')  # 优秀成果标签对应的id
        tag = request.query_params.get('tag')  # 当tag有值时，代表搜索全部未被选为优秀的成果

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 30)  # 验证每页的数量

        # data = models.Projects.objects.values('uuid', 'name', 'classify__cls_name', 'key_word', 'good_mark__remarks',
        #                                       'release_date', 'user__first_name', 'views', 'downloads'
        #                                       ).filter(status=1).order_by('-id')
        data = models.Projects.objects.filter(status=1).order_by('-id')
        if keyword:
            data = data.filter(Q(name__contains=keyword) | Q(key_word__contains=keyword))
            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='优秀成果查询{}'.format(mark_id), user_obj=request.user)
            # -- 记录结束 --

        if tag:
            data = data.filter(good_mark__isnull=True)
        else:
            if mark_id:
                data = data.filter(good_mark=mark_id)

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()
        result = QuerySerializer.GoodProListSerializer(instance=res['res'], many=True)
        res['res'] = result.data
        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def set_good_pro(self, request):
        """
        优秀成果修改（选中或撤销）
        :param request:
        :return:
        """
        # print(request.data)
        param_dict = request.data
        uuid_list = param_dict.get('uuid')  # uuid组成的数组
        mark_id = param_dict.get('mark_id', None)  # 若能获取到mark_id,则代表选中，若没有则代表撤销
        try:
            pro_obj = models.Projects.objects.filter(uuid__in=uuid_list)
            # print(pro_obj, uuid_list, type(uuid_list))
            pro_obj.update(good_mark=mark_id)
            # print('aaaa', mark_id)
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='优秀成果变更:{},{}'.format(str(uuid_list),
                                                                           str(mark_id)), user_obj=request.user)
            # -- 记录结束 --
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/GoodProjectsManageView-post',
                         user=request.user.id, keyword='优秀成果管理失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=False)
    def get_all_mark(self, request):
        """
        优秀成果标志；列表信息获取
        :param request:
        :return:
        """
        keyword = request.query_params.get('kw', '')  # 搜索关键字
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 30)

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 30)  # 验证每页的数量
        data = models.ProjectsMark.objects.values('id', 'remarks').order_by('id')
        if keyword:
            data = data.filter(remarks__contains=keyword)
            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='优秀成果标志查询', user_obj=request.user)
            # -- 记录结束 --

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def set_pro_mark(self, request):
        """
        标签修改、添加、删除
        :param request:
        :return:
        """
        # print(request.data)
        param_dict = request.data
        tag = param_dict.get('tag', 'add')  # tag操作标志add,modify,delete
        mark_id = param_dict.get('mark_id', None)
        remarks = param_dict.get('remarks', None)
        try:
            if tag == 'add':
                models.ProjectsMark.objects.create(remarks=remarks)
            elif tag == 'modify':
                models.ProjectsMark.objects.filter(pk=mark_id).update(remarks=remarks)
            else:
                models.ProjectsMark.objects.filter(pk=mark_id).delete()
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='标签变更:{}'.format(tag), user_obj=request.user)
            # -- 记录结束 --
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/GoodProjectsManageView-post',
                         user=request.user.id, keyword='标签变更失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)

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


class ResearchManageView(viewsets.ViewSet):
    """
    课题搜索（招标搜索）
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    @action(methods=['get'], detail=False)
    def get_research_list(self, request):
        keyword = request.query_params.get('kw', '')
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 8)
        column = request.query_params.get('column', 'name')
        tag = request.query_params.get('tag', 'all')  # 区分公共查看(all)还是个人后台查看(personal)
        org = request.query_params.get('org_id', 0)  # 所属单位筛选
        # print(request.query_params)
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 8)  # 验证每页数量

        data = models.Research.objects.values('id', 'uuid', 'name', 'classify__cls_name', 'start_date', 'end_date',
                                              'user', 'guidelines', 'user__org__name', 'contacts', 'phone', 'user__org',
                                              'status', 'funds').filter(status__in=[0, 1, 2, 3])

        if keyword:
            keyword = str(keyword).replace(' ', '')
            # cls_t不作为检索条件
            if column not in ['name', 'contacts', 'user__org__name']:
                column = 'name'
            cond = {'{}__contains'.format(column): keyword}
            data = data.filter(**cond)
            # print('1', data.query)

        if tag == 'all':
            # 前方页面显示未发布中状态的招标
            data = data.filter(status=1).order_by('-start_date')
        elif tag == 'personal':
            if org:
                # 所属单位筛选
                data = data.filter(user__org=org)
            # -- 权限开始 --
            user = request.user
            data = permission_filter_data(user, data, 'user__org', status__in=[1, 2, 3])

            # -- 权限结束 --
            # 排序
            data = data.order_by('-id')

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        if tag == 'personal':
            for i in range(len(res['res'])):
                if res['res'][i]['status'] == 0:
                    res['res'][i]['edit'] = 1
                else:
                    res['res'][i]['edit'] = 0
                # 统计投标数量
                bid_count = models.Bid.objects.filter(bidder_status=1, bidding=res['res'][i]['id']).count()
                res['res'][i]['bid_count'] = bid_count
                # 统计已审批投标数量
                bid_ed_count = models.Bid.objects.filter(bidder_status__in=[2, 3], bidding=res['res'][i]['id']).count()
                res['res'][i]['bid_ed_count'] = bid_ed_count
                # 统计申请结题数量
                bid_conclusion = models.Bid.objects.filter(conclusion_status=1, bidding=res['res'][i]['id']).count()
                res['res'][i]['bid_conclusion'] = bid_conclusion
                # 统计已审批申请结题数量
                bid_ed_conclusion = models.Bid.objects.filter(
                    conclusion_status__in=[2, 3], bidding=res['res'][i]['id']).count()
                res['res'][i]['bid_ed_conclusion'] = bid_ed_conclusion
                # 将状态改为对应含义
                res['res'][i]['status'] = settings.RESEARCH_STATUS_CHOICE[res['res'][i]['status']]

                group_id_list = get_user_group(request.user)
                user_id = request.user.id if type(request.user) != AnonymousUser else 0

                if settings.GENERAL_ORG_GROUP in group_id_list:
                    # 对普通机构人员的限制（能看全部，仅能编辑自己）
                    if res['res'][i]['user'] == user_id:
                        res['res'][i]['can_be_edit'] = 1
                    else:
                        res['res'][i]['can_be_edit'] = 0
                else:
                    res['res'][i]['can_be_edit'] = 1

        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_research_detail(self, request):
        uuid = request.query_params.get('uuid', '')
        if uuid:
            try:
                data = models.Research.objects.values('id', 'uuid', 'name', 'classify', 'start_date', 'end_date',
                                                      'guidelines', 'funds', 'brief', 'contacts', 'phone',
                                                      'user__org__name').get(uuid=uuid)
                # print(data)
                res = {'res': data}
                return Response(res, status=status.HTTP_200_OK)
            except Exception as e:
                set_run_info(level='error', address='/query/view.py/ResearchDetailView-list',
                             keyword='获取课题详情失败：{}'.format(e))
                res = {'res': '没有找到记录'}
                return Response(res, status=status.HTTP_404_NOT_FOUND)
        else:
            set_run_info(level='error', address='/query/view.py/ResearchDetailView-list',
                         keyword='获取课题详情-参数uuid缺失')
            res = {'res': '缺失参数'}
            return Response(res, status=status.HTTP_404_NOT_FOUND)

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

        data = models.Bid.objects.values('id', 're_title', 'bidder_date', 'bidder_status', 'bidder',
                                         'leader', 'lea_phone', 'contacts', 'con_phone', 'bidding__name',
                                         'conclusion_status').filter(bidding=re_id)
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
        return param_key


class BidManageView(viewsets.ViewSet):
    """
    投标信息管理
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    bid_obj = models.Bid.objects

    @action(methods=['get'], detail=False)
    def get_personal_bid(self, request):
        """
        获得所有个人所属投标的id和标题--已中标的
        :param request:
        :return:
        """
        user = request.user
        if user.is_active:
            data = BidManageView.bid_obj.values(
                'id', 're_title').filter(submitter=user.id, bidder_status=2).order_by('-id')
            # print(data.query)
        else:
            data = ''
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_personal_bid_list(self, request):
        """
        获取能够管理的投标列表--后台
        :param request:
        :return:
        """
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        keyword = request.query_params.get('kd', '')
        bid_status = request.query_params.get('status', 100)  # 100代表未输入
        org = request.query_params.get('org_id', 0)  # 所属单位筛选
        user = request.user
        # print(user)
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 30)  # 验证每页的数量
        bid_status = self.try_except(bid_status, 100)  # 验证状态,筛选用

        data = BidManageView.bid_obj.values(
            'id', 'bidding__name', 're_title', 'bidder_date', 'bidder_status', 'submitter',
            'funds', 'contacts', 'con_phone', 'conclusion_status').exclude(bidder_status=4).order_by('-id')

        if keyword:
            data = data.filter(Q(bidding__name__contains=keyword) | Q(re_title__contains=keyword) |
                               Q(bidder_date__contains=keyword) | Q(funds__contains=keyword) |
                               Q(contacts__contains=keyword) | Q(con_phone__contains=keyword))

            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='搜索投标信息', user_obj=user)
            # -- 记录结束 --

        if bid_status != 100:
            # 状态筛选
            data = data.filter(bidder_status=bid_status)

        if org:
            # 所属单位筛选
            data = data.filter(submitter__org=org)

        # -- 权限开始 --
        data = permission_filter_data(user, data, 'submitter__org', bidder_status__in=[1, 2, 3])
        if not data:
            return Response(status=status.HTTP_200_OK)
        # -- 权限结束 --

        # print(data.count())
        sp = SplitPages(data, page, page_num)
        res = sp.split_page()
        for i in range(len(res['res'])):
            res['res'][i]['bidder_status'] = settings.BIDDER_STATUS_CHOICE[res['res'][i]['bidder_status']]
            group_id_list = get_user_group(user)
            user_id = user.id if type(user) != AnonymousUser else 0
            if settings.GENERAL_ORG_GROUP in group_id_list:
                # 对普通机构人员的限制（能看全部，仅能编辑自己）
                if res['res'][i]['submitter'] == user_id:
                    res['res'][i]['can_be_edit'] = 1
                else:
                    res['res'][i]['can_be_edit'] = 0
            else:
                res['res'][i]['can_be_edit'] = 1
        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_specified_bid_list(self, request):
        """
        获得指定类型的投标列表--首页
        :param request:
        :return:
        """
        keyword = request.query_params.get('kw', '')  # 搜索关键字
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 8)
        column = request.query_params.get('column', 're_title')  # 're_title名称', 'bidder单位', 'leader负责人'
        tag = request.query_params.get('tag', 'doing')  # 课题推进doing还是课题结题done
        # print(request.query_params)
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 8)  # 验证每页数量
        data = BidManageView.bid_obj.values('id', 're_title', 'bidder', 'bidding__classify__cls_name', 'leader',
                                            'bidder_date__year', 'bidder_status', 'conclusion_status').order_by('-id')

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
            pro_id_obj = models.Projects.objects.values('id').filter(bid=res['res'][i]['id'], status=1)
            if pro_id_obj:
                pro_id_list = [i['id'] for i in pro_id_obj]
                par_sum = models.ProRelations.objects.values('par').filter(pro__in=pro_id_list).distinct().count()
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
            set_run_info(level='error', address='/query/view.py/MyBidQueryView-list',
                         keyword='强转参数出错{}'.format(e))
        return param_key


class ParQueryView(viewsets.ViewSet):
    """
    后台-专家检索
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    @action(methods=['get'], detail=False)
    def get_personal_par(self, request):
        """
        获得本机构以及下级机构的研究人员
        :param request:
        :return:
        """
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        keyword = request.query_params.get('kw', '')

        page = self.try_except(page, 1)  # 验证类型
        page_num = self.try_except(page_num, 10)  # 验证返回数量

        data = models.Participant.objects.values('id', 'uuid', 'name', 'unit__name', 'job', 'email'
                                                 ).exclude(is_show=0).order_by('-id')

        # -- 权限开始 --
        user = request.user
        data = permission_filter_data(user, data, 'unit', module="par_manage")
        if not data:
            return Response(status=status.HTTP_200_OK)
        # -- 权限结束 --

        if keyword:
            data = data.filter(Q(name__contains=keyword) | Q(unit__name__contains=keyword) |
                               Q(job__contains=keyword) | Q(email__contains=keyword))

            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='后台-搜索人员信息', user_obj=request.user)
            # -- 记录结束 --

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        for i in range(len(res['res'])):
            group_id_list = get_user_group(user)
            if settings.GENERAL_ORG_GROUP in group_id_list:
                # 对普通机构人员的限制（能看全部，仅能编辑自己）--不可编辑研究人员
                res['res'][i]['can_be_edit'] = 0
            else:
                res['res'][i]['can_be_edit'] = 1

        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_par_list(self, request):
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 8)
        name = request.query_params.get('name', '')
        par_id = request.query_params.get('par_id', '')

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 8)  # 验证每页的数量

        if par_id:
            data = models.Participant.objects.values('id', 'name', 'unit', 'brief', 'job', 'pro_sum', 'photo'
                                                     ).filter(pk=par_id, is_show=True)
        else:
            data = models.Participant.objects.values('id', 'name', 'unit', 'pro_sum'
                                                     ).filter(is_show=True).order_by('id')
            if name:
                data = data.filter(name__contains=name)

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        for i in range(len(res['res'])):
            if res['res'][i]['unit']:
                res['res'][i]['unit'] = models.Organization.objects.get(pk=res['res'][i]['unit']).name
            # 个人总评分
            res['res'][i]['score_num'] = \
                models.ProRelations.objects.filter(par_id=res['res'][i]['id'], is_eft=True).aggregate(Sum('score'))[
                    'score__sum']
            speciality_list = models.ProRelations.objects.values('speciality').filter(par_id=res['res'][i]['id'])
            speciality = ''
            for i_dict in speciality_list:
                if i_dict['speciality']:
                    speciality += '{};'.format(i_dict['speciality'])
            # 专业特长
            res['res'][i]['speciality'] = speciality
            pro_id_list = models.ProRelations.objects.values('pro_id').filter(par_id=res['res'][i]['id'], is_eft=True)
            pro_id_list_fin = [i_dict['pro_id'] for i_dict in pro_id_list]
            # 成果总浏览量
            res['res'][i]['view_sum'] = \
                models.Projects.objects.filter(id__in=pro_id_list_fin, status=1).aggregate(Sum('views'))[
                    'views__sum']
            # 成果总下载量
            res['res'][i]['download_sum'] = \
                models.Projects.objects.filter(id__in=pro_id_list_fin, status=1).aggregate(Sum('downloads'))[
                    'downloads__sum']
        return Response(res, status=status.HTTP_200_OK)

    # --- 升级专家开始--
    @action(methods=['post'], detail=False)
    def set_par_re_pro(self, request):
        """
        研究人员认证成果
        :return:
        """
        param_dict = request.data
        user = request.user
        user_id = user.id if type(user) != AnonymousUser else 0
        par_id = user.par.id if user.par else None
        param_dict['par'] = par_id
        # print('--11', param_dict)
        try:
            serialier_param = QuerySerializer.ParReProCreateSerializer(data=param_dict)
            serialier_param.is_valid(raise_exception=True)
            serialier_param.save()
        except AttributeError as e:
            set_run_info(level='error', address='/query/view.py/ParQueryView-set_par_re_pro',
                         user=user_id, keyword='研究人员认证成果：{}'.format(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=False)
    def get_par_pro_list(self, request):
        """
        个人参与的成果展示、包括认证的
        :return:
        """
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        # kw = request.query_params.get('kw')
        user = request.user

        if type(user) == AnonymousUser:
            set_run_info(level='error', address='/query/view.py/ParQueryView-get_par_to_vip_list',
                         keyword='获取个人参与的成果展示失败：获取不到user')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if user.par:
            par_id = user.par.id
        else:
            set_run_info(level='error', address='/query/view.py/ParQueryView-get_par_to_vip_list',
                         keyword='获取个人参与的成果展示失败：获取不到par')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 10)  # 验证每页的数量

        data1 = models.ProRelations.objects.values(
            'pro__uuid', 'pro__name', 'pro__key_word', 'pro_source').filter(par=par_id, is_eft=True)
        data2 = models.ParRePro.objects.values(
            'id', 'pro__uuid', 'pro__name', 'pro__key_word', 'support_materials').filter(par=par_id)
        data = []
        data.extend(data1)
        data.extend(data2)

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()
        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def apply_par_to_vip(self, request):
        """
        研究人员升级大V申请
        :param request:
        :return:
        """
        user = request.user
        if type(user) == AnonymousUser:
            set_run_info(level='error', address='/query/view.py/ParQueryView-apply_par_to_vip',
                         keyword='研究人员升级大V申请失败：获取不到user')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if user.par:
            par_obj = user.par
        else:
            set_run_info(level='error', address='/query/view.py/ParQueryView-apply_par_to_vip',
                         keyword='研究人员升级大V申请失败：获取不到par')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            models.ParToVIP.objects.create(par=par_obj)
            return Response(status=status.HTTP_201_CREATED)
        except AttributeError as e:
            set_run_info(level='error', address='/query/view.py/ParQueryView-apply_par_to_vip',
                         user=user.id, keyword='研究人员升级大V申请：{}'.format(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def get_par_to_vip_list(self, request):
        """
        获得研究人员升级大V审批列表
        :param request:
        :return:
        """
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        result = request.query_params.get('result', 0)  # 状态

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 10)  # 验证每页的数量

        data = models.ParToVIP.objects.values('id', 'par__name', 'created_date').filter(result=result)

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()
        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def set_par_to_vip(self, request, pk):
        """
        研究人员升级大V审批
        :param request:
        :param pk:
        :return:
        """
        param_dict = request.data
        result = param_dict.get('status')  # 1：通过 2：否决  0：未处理
        remarks = param_dict.get('remarks')  # 备注
        try:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            item_tmp = models.ParToVIP.objects.filter(id=pk)
            if int(result) == 1:
                # 同意
                if item_tmp:
                    item_obj = item_tmp[0]
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)

                # 更新人员表信息
                par_obj = item_obj.par
                par_obj.level = item_obj.level
                par_obj.save()

                item_tmp.update(result=1, remarks=remarks, approval_date=current_time)
            else:
                # 驳回账号
                item_tmp.update(result=2, remarks=remarks, approval_date=current_time)
            add_user_behavior(keyword='', search_con='研究人员升级大V审批({}:{})'.format(pk, result),
                              user_obj=request.user)
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/ParQueryView-set_par_to_vip',
                         keyword='研究人员升级大V审批失败：{}'.format(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

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

    @action(methods=['GET'], detail=True)
    def get_verity_file(self, request, pk):
        """
        查看在职证明材料
        :param request:
        :param pk:
        :return:
        """
        try:
            obj = models.ParRePro.objects.get(id=pk)
            the_file_name = 'a.pdf'
            download_url_fin = os.path.join(settings.MEDIA_ROOT, str(obj.support_materials))
            # 将汉字换成ascii码，否则下载名称不能正确显示
            the_file_name = urllib.parse.quote(the_file_name)
            response = StreamingHttpResponse(self.file_iterator(download_url_fin))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(the_file_name)
            return response
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/ParQueryView-get_verity_file',
                         keyword='查看在职证明材料失败：{}'.format(e))
            return Response({'msg': "查看在职证明材料失败", "status": 404}, status=status.HTTP_200_OK)

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

    @action(methods=['get'], detail=False)
    def get_pro_list(self, request):
        """
        获得所有成果列表
        :param request:
        :return:
        """
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        kw = request.query_params.get('kw')

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 10)  # 验证每页的数量

        data = models.Projects.objects.values('id', 'name').filter(status=1)
        if kw:
            data = data.filter(name__contains=kw)
        sp = SplitPages(data, page, page_num)
        res = sp.split_page()
        return Response(res, status=status.HTTP_200_OK)
    # --- 升级专家结束-


class OrgQueryView(viewsets.ViewSet):
    """
    机构检索-后台+成果填写推荐
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    @action(methods=['get'], detail=False)
    def get_personal_org(self, request):
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        keyword = request.query_params.get('kw', '')

        page = self.try_except(page, 1)  # 验证类型
        page_num = self.try_except(page_num, 10)  # 验证返回数量

        data = models.Organization.objects.filter(is_show=True).order_by('-id')

        # -- 权限开始 --
        user = request.user
        data = permission_filter_data(user, data, 'id')
        if not data:
            return Response(status=status.HTTP_200_OK)
        # -- 权限结束 --

        if keyword:
            data = data.filter(Q(name__contains=keyword) | Q(nature__remarks__contains=keyword))

            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='后台-搜索机构信息', user_obj=request.user)
            # -- 记录结束 --

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        result = UploadsSerializer.OrgPersonalListSerializer(instance=res['res'], many=True)
        res['res'] = result.data
        # print(result.data)

        for i in range(len(res['res'])):
            group_id_list = get_user_group(user)
            if settings.GENERAL_ORG_GROUP in group_id_list:
                # 对普通机构人员的限制（能看全部，仅能编辑自己）--不可编辑机构
                res['res'][i]['can_be_edit'] = 0
            else:
                res['res'][i]['can_be_edit'] = 1

        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_org_list(self, request):
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 8)
        unit = request.query_params.get('unit', '')
        org_id = request.query_params.get('org_id', 0)
        # a_b = request.query_params.get('roles', 'b')
        # print(request.query_params)
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 8)  # 验证每页的数量
        org_id = self.try_except(org_id, 0)  # 验证id
        subordinate_org_obj = []
        subordinate_org_count = 0
        subordinate_org_pro_sum = 0
        if org_id:
            data = models.Organization.objects.values('id', 'name', 'brief', 'pro_sum', 'par_sum', 'photo'
                                                      ).filter(pk=org_id, is_show=True)
            # print(data)
            if data:
                # 获得本机构及其下属机构id列表
                subordinate_org_list = self.get_relative_org_list(data.first()['id'])
                subordinate_org_obj = models.Organization.objects.values(
                    'id', 'name', 'pro_sum').filter(pk__in=subordinate_org_list, is_show=True)
                subordinate_org_count = len(subordinate_org_list)
                for sub_org in subordinate_org_obj:
                    subordinate_org_pro_sum = subordinate_org_pro_sum + sub_org['pro_sum']
        else:
            data = models.Organization.objects.values(
                'id', 'name', 'pro_sum', 'par_sum', 'nature__remarks').filter(is_show=True).order_by('id')

            if unit:
                data = data.filter(name__contains=unit)
        # print(data.query)
        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        for i in range(len(res['res'])):
            # 机构总评分
            score_sum = \
                models.ProRelations.objects.filter(org_id=res['res'][i]['id'], is_eft=True).aggregate(Sum('score'))[
                    'score__sum']
            if score_sum:
                res['res'][i]['score_sum'] = '%.2f' % score_sum
            else:
                res['res'][i]['score_sum'] = 0
            # 成果总浏览量
            res['res'][i]['view_sum'] = models.Projects.objects.filter(status=1).filter(
                Q(lead_org__id=res['res'][i]['id']) | Q(research__id=res['res'][i]['id'])).aggregate(Sum('views'))[
                'views__sum']
            # 成果总下载量
            res['res'][i]['download_sum'] = models.Projects.objects.filter(status=1).filter(
                Q(lead_org__id=res['res'][i]['id']) | Q(research__id=res['res'][i]['id'])).aggregate(Sum('downloads'))[
                'downloads__sum']
            # print(a)

        if org_id:
            res['subordinate_org_obj'] = subordinate_org_obj
            res['subordinate_org_count'] = subordinate_org_count
            res['subordinate_org_pro_sum'] = subordinate_org_pro_sum

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

    @staticmethod
    def get_relative_org_list(ori_org_id):
        """
        获得本机构所有下级机构,不包括本机构
        :param ori_org_id: 初始机构id
        :return:
        """
        org_id_list = [ori_org_id]
        if org_id_list:
            for org_id in org_id_list:
                org_id_list_tmp = models.Organization.objects.values('id').filter(superior_unit=org_id, is_show=True)
                org_id_list_tmp_list = [j['id'] for j in org_id_list_tmp]
                if org_id_list_tmp_list:
                    org_id_list.extend(org_id_list_tmp_list)
        org_id_list.remove(ori_org_id)
        return org_id_list


class MyUserView(viewsets.ViewSet):
    """
    后台-用户管理
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

        data = models.User.objects.values('id', 'username', 'first_name', 'is_active').order_by('-id')

        # -- 权限开始 --
        user = request.user
        data = permission_filter_data(user, data, 'org', module="user_manage")
        if not data:
            return Response(status=status.HTTP_200_OK)
        # else:
        #     return Response(status=status.HTTP_200_OK)

        if keyword:
            data = data.filter(Q(username__contains=keyword) | Q(first_name__contains=keyword))

            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='搜索用户信息', user_obj=request.user)
            # -- 记录结束 --

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        group_id_list = get_user_group(user)
        user_id = user.id if type(user) != AnonymousUser else 0

        for i in range(len(res['res'])):

            roles_obj = models.User.objects.get(id=res['res'][i]['id']).groups.all().first()
            res['res'][i]['roles'] = roles_obj.name if roles_obj else None

            if settings.GENERAL_ORG_GROUP in group_id_list:
                # 对普通机构人员的限制（能看全部，仅能编辑自己）
                if res['res'][i]['id'] == user_id:
                    res['res'][i]['can_be_edit'] = 1
                else:
                    res['res'][i]['can_be_edit'] = 0
            else:
                res['res'][i]['can_be_edit'] = 1

        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def get_user_detail(self, request, pk):
        """
        用户详情
        :param request:
        :param pk: 用户id
        :return:
        """
        # print(request)
        data = models.User.objects.filter(id=pk)
        if data:
            data_fin = QuerySerializer.UserRetrieveSerializer(instance=data[0])
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='查看用户信息详情({})'.format(pk),
                              user_obj=request.user)
            # -- 记录结束 --
            return Response(data_fin.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def create(request):
        """
        创建用户
        :param request:
        :return:
        """
        param_dict = request.data
        id_card = param_dict.get('id_card')  # 身份证号
        first_name = param_dict.get('first_name')  # 真实姓名
        username = param_dict.get('username')  # 用户名
        password = param_dict.get('password')
        org_id = param_dict.get('org_id', 0)
        org_name = param_dict.get('org')
        par_id = param_dict.get('par_id')
        roles = int(param_dict.get('roles', 0))  # 角色
        phone = param_dict.get('phone')  # 手机号
        email = param_dict.get('email')  # 邮箱
        # print(param_dict)
        org_obj = None
        par_obj = None
        if roles in [settings.FIRST_LEVEL_MANAGER_GROUP, settings.GENERAL_ORG_GROUP]:
            org_name = org_name.replace(' ', '')
            org_id = org_id if org_id else 0
            org_obj_list = models.Organization.objects.filter(id=org_id, name=org_name)
            if org_obj_list:
                org_obj = org_obj_list[0]
                # 验证机构和机构管理员是否存在
                if roles == settings.FIRST_LEVEL_MANAGER_GROUP:
                    user_obj = models.User.objects.filter(org=org_obj)
                    user_id_list = [j.id for j in user_obj]
                    group_id_obj = Group.objects.filter(user__in=user_id_list, id=settings.FIRST_LEVEL_MANAGER_GROUP)
                    if group_id_obj:
                        # 本机构管理员已存在
                        return Response({"msg": "本机构管理员已存在", "status": 403}, status=status.HTTP_200_OK)
            else:
                # 机构不存在
                return Response({"msg": "找不到机构", "status": 404}, status=status.HTTP_200_OK)
        elif roles in [settings.EXPERT_PER_GROUP]:
            # 验证人员存在
            par_obj_list = models.Participant.objects.filter(id=par_id)
            if par_obj_list:
                par_obj = par_obj_list[0]
            else:
                # 人员不存在
                return Response({"msg": "找不到人员", "status": 404}, status=status.HTTP_200_OK)

        password_end = make_password(password, None, 'pbkdf2_sha256')  # 源字符串，固定字符串，加密方式
        try:
            user_obj = models.User.objects.create(
                first_name=first_name,
                username=username,
                password=password_end,
                org=org_obj,
                id_card=id_card,
                cell_phone=phone,
                email=email,
                par=par_obj
            )
            # 添加组
            if roles:
                # 添加角色组
                groups_list = [roles]
                groups_list_obj = Group.objects.filter(id__in=groups_list)
                user_obj.groups.add(*groups_list_obj)

            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='新增用户信息({})'.format(user_obj.id), user_obj=request.user)
            # -- 记录结束 --

            return Response({"msg": "创建成功", "status": 201}, status=status.HTTP_201_CREATED)
        except Exception as e:
            # 创建失败
            set_run_info(level='error', address='/query/view.py/MyUserView-create',
                         user=request.user.id, keyword='新增用户信息失败：{}'.format(e))
            return Response({"msg": "创建失败", "status": 500}, status=status.HTTP_200_OK)

    @staticmethod
    def put(request):
        """
        用户信息修改
        :param request:
        :return:
        """
        param_dict = request.data
        user_id = param_dict.get('user_id')
        is_active = param_dict.get('is_active', 1)
        phone = param_dict.get('phone')  # 手机号
        email = param_dict.get('email')  # 邮箱
        photo = request.FILES.get('photo')  # 头像
        # print(param_dict)

        try:
            if photo:
                current_year = datetime.datetime.now().year
                current_month = '{:02d}'.format(datetime.datetime.now().month)
                photo_save_path_dirs = os.path.join(os.path.join(settings.MEDIA_ROOT, 'user'), 'portrait')
                file_obj = UploadFile(photo_save_path_dirs, photo)
                photo_name_fin = file_obj.handle()

                models.User.objects.filter(id=user_id).update(
                    cell_phone=phone,
                    is_active=is_active,
                    email=email,
                    photo='user/portrait/{}/{}/{}'.format(current_year, current_month, photo_name_fin)
                )
            else:
                models.User.objects.filter(id=user_id).update(
                    cell_phone=phone,
                    is_active=is_active,
                    email=email,
                )
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='编辑用户信息({}):{}'.format(user_id, str(param_dict)),
                              user_obj=request.user)
            # -- 记录结束 --
            return Response({"msg": "编辑成功", "status": 200}, status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/MyUserView-update',
                         user=request.user.id, keyword='编辑用户信息失败：{}'.format(e))
            return Response({"msg": "编辑失败", "status": 500}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def apply_user_to_par(self, request):
        """
        研究人员认证
        :param request:
        :return:
        """
        param_dict = request.data
        user = request.user
        user_id = user.id if type(user) != AnonymousUser else 0
        param_dict['user'] = user_id
        # print('--11', param_dict)
        try:
            serialier_param = QuerySerializer.UserToParCreateSerializer(data=param_dict)
            serialier_param.is_valid(raise_exception=True)
            serialier_param.save()
        except AttributeError as e:
            set_run_info(level='error', address='/query/view.py/MyUserView-set_user_to_participant',
                         user=user_id, keyword='研究人员认证：{}'.format(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=False)
    def get_user_to_par_list(self, request):
        """
        研究人员认证列表--平台管理员和超管可见
        :param request:
        :return:
        """
        param_dict = request.query_params
        page = param_dict.get('page', 1)
        page_num = param_dict.get('page_num', 10)
        keyword = param_dict.get('kw', '')
        up_status = param_dict.get('up_status', 0)

        page = self.try_except(page, 1)  # 验证类型
        page_num = self.try_except(page_num, 10)  # 验证返回数量

        data = models.UserToParticipant.objects.filter(up_status=up_status)

        if keyword:
            data = data.filter(Q(user__username__contains=keyword) | Q(user__first_name__contains=keyword))

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()

        result = QuerySerializer.UserToParListSerializer(instance=res['res'], many=True)
        res['res'] = result.data

        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def set_user_to_par(self, request, pk):
        """
        审批-研究人员认证--平台管理员和超管可见
        :param request:
        :param pk:
        :return:
        """
        param_dict = request.data
        up_status = param_dict.get('status')  # 1：通过 2：否决  0：未处理
        remarks = param_dict.get('remarks')  # 备注
        try:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            item_tmp = models.UserToParticipant.objects.filter(id=pk)
            if int(up_status) == 1:
                # 同意
                if item_tmp:
                    item_obj = item_tmp[0]
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
                # 获取关联人员id
                user_obj = item_obj.user
                par_info = self.choose_or_create_par(user_obj)

                par_id = par_info.get("par_id")
                if par_id == '-1':
                    return Response(status=status.HTTP_404_NOT_FOUND)
                # 更新用户信息（挂人员）
                par_obj = models.Participant.objects.get(id=par_id)
                user_obj.par = par_obj
                user_obj.save()

                # 更换角色组（普通个人换为专家个人）
                groups_list_obj = Group.objects.filter(id=settings.EXPERT_PER_GROUP)
                user_obj.groups.clear()
                user_obj.groups.add(*groups_list_obj)

                # 更新研究人员信息
                self.update_par_info(par_obj, item_obj)

                item_tmp.update(up_status=1, remarks=remarks, approval_date=current_time)
            else:
                # 驳回账号
                item_tmp.update(up_status=2, remarks=remarks, approval_date=current_time)
            add_user_behavior(keyword='', search_con='认证研究人员审批({}:{})'.format(pk, up_status),
                              user_obj=request.user)
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/MyUserView-set_user_to_par',
                         keyword='认证研究人员审批失败：{}'.format(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_user_to_par_detail(self, request):
        """
        用户认证研究人员详情
        :param request:
        :return:
        """
        pk_id = request.query_params.get('pk_id', 0)
        tag = request.query_params.get('tag', 'utp')  # utp:认证研究人员  user:用户
        if tag == 'utp':
            data = models.UserToParticipant.objects.filter(id=pk_id)
        else:
            data = models.UserToParticipant.objects.filter(user=pk_id).order_by('-id')  # 取多次的最新结果
        if data:
            data_fin = QuerySerializer.UserToParRetrieveSerializer(instance=data[0])
            # -- 记录开始 --
            add_user_behavior(keyword='', search_con='查看用户认证研究人员详情({}:{})'.format(tag, pk_id),
                              user_obj=request.user)
            # -- 记录结束 --
            return Response(data_fin.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

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

    @staticmethod
    def choose_or_create_par(user_obj):
        """
        选择或者创建人员。并返回人员id
        :param user_obj: 申请用户对象
        :return:{"msg": 成功标志, "par_id": par对应id}
        """
        par_id_card_code = user_obj.id_card
        par_info = {"msg": 0, "par_id": -1}
        if par_id_card_code:
            par_obj = models.Participant.objects.filter(id_card=par_id_card_code)
            if par_obj:
                # 人员库里面有直接挂
                par_id = par_obj.first().id
            else:
                # 人员库里面没有啧创建
                par_obj_tmp = models.Participant.objects.create(id_card=par_id_card_code, name=user_obj.first_name)
                par_id = par_obj_tmp.id
            par_info["msg"] = 1
            par_info["par_id"] = par_id
        else:
            set_run_info(level='error', address='/login/view.py/RegisterView-set_register_user',
                         keyword='注册账号审批失败：{}'.format('注册信息中没有机构信用码'))
        return par_info

    @staticmethod
    def update_par_info(par_obj, item_obj):
        """
        同步更新人员信息--有则更新，无则不变
        :param par_obj: 研究人员对象
        :param item_obj:待审批对象
        :return:
        """
        update_dict = dict()
        update_dict["cell_phone"] = item_obj.user.cell_phone
        update_dict["email"] = item_obj.user.email
        update_dict["gender"] = item_obj.gender
        update_dict["birth"] = item_obj.birth
        update_dict["education"] = item_obj.education
        update_dict["academic_degree"] = item_obj.academic_degree
        update_dict["address"] = item_obj.address
        update_dict["postcode"] = item_obj.postcode
        update_dict["brief"] = item_obj.brief
        update_dict["research_direction"] = item_obj.research_direction
        update_dict["photo"] = item_obj.photo
        update_dict["id_card_photo_positive"] = item_obj.id_card_photo_positive
        update_dict["id_card_photo_reverse"] = item_obj.id_card_photo_reverse
        # 清除字典中值为空的键值对
        for k in list(update_dict.keys()):  # 对字典update_dict中的keys，相当于形成列表list
            if not update_dict[k]:
                del update_dict[k]
        # print(update_dict)
        par_obj.__dict__.update(**update_dict)
        par_obj.save()

    @action(methods=['GET'], detail=True)
    def get_verity_file(self, request, pk):
        """
        查看在职证明材料
        :param request:
        :param pk:
        :return:
        """
        try:
            obj = models.UserToParticipant.objects.get(id=pk)
            the_file_name = 'a.pdf'
            download_url_fin = os.path.join(settings.MEDIA_ROOT, str(obj.job_certi))
            # 将汉字换成ascii码，否则下载名称不能正确显示
            the_file_name = urllib.parse.quote(the_file_name)
            response = StreamingHttpResponse(self.file_iterator(download_url_fin))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(the_file_name)
            return response
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/MyUserView-get_verity_file',
                         keyword='查看在职证明材料失败：{}'.format(e))
            return Response({'msg': "查看在职证明材料失败", "status": 404}, status=status.HTTP_200_OK)

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
            num = 10
        latest_date = list(models.HotWords.objects.values('create_date').order_by('-create_date')[:1])[0]['create_date']
        param = models.HotWords.objects.values('hot_word').filter(
            is_true=True, create_date=latest_date).order_by('num')[:num]
        res = {'res': param}
        return Response(res, status=status.HTTP_200_OK)
