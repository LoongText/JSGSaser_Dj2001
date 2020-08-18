from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from tables.models import Projects, Research, Participant, ProRelations, Organization, UserClickBehavior, User
from tables.models import HotWords, Bid
from django.contrib.auth .models import Group
from django.db.models import Sum, Count, Q
import datetime
# import logging as log
from login.auth import ExpiringTokenAuthentication
from query.split_page import SplitPages
# import json
from jsg.settings import ORG_NATURE_LOWER_LEVEL, ORG_NATURE_HIGHER_LEVEL
from jsg.settings import ORG_GROUP_LOWER_LEVEL, ORG_GROUP_MANAGER_LEVEL, ORG_GROUP_SUPERUSER_LEVEL
from backstage.views import add_user_behavior
from login.views import set_run_info

# logger = log.getLogger('django')


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
        if org_id and not par_id:
            # 指定机构查询
            lead_org_data = data.filter(lead_org__id=org_id)
            re_org_data = data.filter(research__id=org_id)
            lead_org_data_list = []
            re_org_data_list = []
            if lead_org_data:
                lead_org_data_list = [i['id'] for i in lead_org_data]
            if re_org_data:
                re_org_data_list = [i['id'] for i in re_org_data]
            all_org_list_set = set(lead_org_data_list + re_org_data_list)
            # data = data.filter(Q(research__id=org_id) | Q(lead_org__id=org_id))
            data = data.filter(id__in=all_org_list_set)

        elif par_id and not org_id:
            # 指定人员查询
            relation_data = ProRelations.objects.values('pro').filter(is_eft=1, par=par_id).distinct('pro')
            # print('***', relation_data.query)
            pro_id_list = [i['pro'] for i in relation_data]
            data = data.filter(id__in=pro_id_list)

        if s_date and s_date != 'NaN-NaN-NaN' and s_date != 'null':
            # 判断日期
            if e_date and e_date != 'NaN-NaN-NaN' and e_date != 'null':
                data = data.filter(release_date__gte=s_date, release_date__lte=e_date)
            else:
                data = data.filter(release_date__gte=s_date)
        else:
            if e_date and e_date != 'NaN-NaN-NaN' and e_date != 'null':
                data = data.filter(release_date__lte=e_date)

        if keyword:
            keyword = str(keyword).replace(' ', '')
            column_kd = '{}__contains'.format(column)
            if cls_t == 100:
                # cls_t不作为检索条件
                data = data.filter(**{column_kd: keyword})
                print('111', data.query)
            else:
                data = data.filter(classify=cls_t).filter(**{column_kd: keyword})
                print('222', data.query)

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
                # print('add user_behavior data', e)
                set_run_info(level='error', address='/query/view.py/ProjectsQueryView-list',
                             user=user_id, keyword='搜索成果-添加行为记录失败：{}'.format(e))
                # logger.info('query 添加行为记录 --未获取到用户id：{}'.format(user_id))
        else:
            if cls_t != 100:
                # cls_t不作为检索条件
                data = data.filter(classify=cls_t)
                print('333', data.query)

        org_obj = ''
        par_obj = ''
        if org_id and not par_id:
            # 机构研究人员姓名
            par_obj = Participant.objects.values('id', 'name').filter(unit__id=org_id, is_show=True)
        elif par_id and not org_id:
            pass
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
            data = data.order_by('-release_date')
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
        print('query_', org_level)
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
            # org_list = [i.name for i in research_org]
            # 判断添加研究机构
            for r_org in research_org:
                if r_org.nature.level in org_level_list:
                    org_list.append(r_org.name)
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
        print('-----', user_id)
        # user = request.user

        user_obj = self.get_user_obj(user_id)  # 获取用户对象
        org_level = get_user_org_level(user_id)  # 获取机构等级
        print('pro detail', org_level)
        # print(uuid)
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
            # print(lead_org_obj)
            # print(research_org_obj)
            lead_org_list = []
            research_org_list = []
            if org_level == ORG_NATURE_HIGHER_LEVEL:
                par_id_obj = ProRelations.objects.values(
                    'id', 'par__name', 'roles', 'speciality', 'job', 'task', 'org__name').filter(
                    pro=obj.id, par__id__isnull=False).order_by('roles')
                if lead_org_obj:
                    # 判断添加牵头机构
                    for l_org in lead_org_obj:
                        # print(l_org, type(l_org))
                        lead_org_list.append(l_org.name)
                if research_org_obj:
                    # 判断添加研究机构
                    for r_org in research_org_obj:
                        # print(r_org, type(r_org))
                        research_org_list.append(r_org.name)
                UserClickBehavior.objects.create(user=user_obj, pro=obj)  # 创建点击记录
            else:
                print(2222)
                par_id_obj = ProRelations.objects.values(
                    'par__name', 'roles', 'speciality', 'job', 'task', 'org__name').filter(
                    pro=obj.id, par__id__isnull=False, org__nature__level__in=[4]).order_by('roles')
                if lead_org_obj:
                    # 判断添加牵头机构
                    for l_org in lead_org_obj:
                        print('222-1', l_org, l_org.nature.level)
                        if l_org.nature.level not in [1, 2, 3]:
                            lead_org_list.append(l_org.name)
                if research_org_obj:
                    # 判断添加研究机构
                    for r_org in research_org_obj:
                        print('222-2', r_org, r_org.nature.level)
                        if r_org.nature.level not in [1, 2, 3]:
                            research_org_list.append(r_org.name)
                UserClickBehavior.objects.create(pro=obj)  # 创建点击记录

            # if par_id_obj:
            #     for i in range(len(par_id_obj)):
            #         print(par_id_obj[i]['id'], par_id_obj[i]['par'])
            #         par_obj = Participant.objects.get(pk=par_id_obj[i]['par'])
            #         print('par_obj:', par_obj.name)
            #         par_id_obj[i]['par'] = par_obj.name
            #         if par_obj.unit:
            #             par_id_obj[i]['unit'] = par_obj.unit.name
            #         else:
            #             par_id_obj[i]['unit'] = None
            cls_t = ''
            if obj.classify:
                cls_t = obj.classify.cls_id

            obj.views_num_update()  # 浏览量+1

            research_org_str = ';'.join(research_org_list)
            lead_org_str = ';'.join(lead_org_list)
            obj_dict = {"lead_org": lead_org_str, "research": research_org_str, "key_word": obj.key_word,
                        "release_date": obj.release_date, "abstract": obj.abstract,
                        "attached": str(obj.attached), "classify": cls_t,
                        "reference": str(obj.reference).split(';'), "par": par_id_obj, 'name': obj.name
                        }
            # print(obj_dict)
            # 将类型id转化为类型具体名称
            # 将参考文献分成列表
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


class ResearchQueryView(viewsets.ViewSet):
    """
    课题搜索（招标搜索）
    """

    def list(self, request):
        keyword = request.query_params.get('kw', '')
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 8)
        column = request.query_params.get('column', 'name')
        # print(request.query_params)
        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 8)  # 验证每页数量

        data = Research.objects.values('id', 'uuid', 'name', 'classify__cls_name', 'start_date', 'end_date',
                                       'guidelines', 'user__org__name', 'contacts', 'phone'
                                       ).filter(status__in=[1, 2, 3]).order_by('-start_date')

        if keyword:
            keyword = str(keyword).replace(' ', '')
            # cls_t不作为检索条件
            if column not in ['name', 'contacts', 'user__first_name']:
                column = 'name'
            cond = {'{}__contains'.format(column): keyword}
            data = data.filter(**cond)
            # print('1', data.query)

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

    @staticmethod
    def post(request):
        # 修改
        param_dict = request.data
        uuid = param_dict.get('uuid', '')
        name = param_dict.get('name', '')
        classify = param_dict.get('classify', 5)
        start_date = param_dict.get('start_date', '')
        end_date = param_dict.get('end_date', '')
        guidelines = param_dict.get('guidelines', '')
        re_status = param_dict.get('status', 0)
        funds = param_dict.get('funds', 0)
        contacts = param_dict.get('contacts', '')
        phone = param_dict.get('phone', '')
        brief = param_dict.get('brief', '')
        # print('guuuuu', guidelines)
        re_obj = Research.objects.filter(uuid=uuid)
        try:
            if guidelines:
                re_obj.update(name=name, classify=classify, start_date=start_date, funds=funds, contacts=contacts,
                              end_date=end_date, guidelines=guidelines, phone=phone, brief=brief, status=re_status)
            else:
                re_obj.update(name=name, classify=classify, start_date=start_date, funds=funds, contacts=contacts,
                              end_date=end_date, phone=phone, brief=brief, status=re_status)
            return Response(1, status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/ResearchDetailView-post',
                         keyword='修改课题详情失败：{}'.format(e))
            return Response(0, status=status.HTTP_200_OK)


class MyBidQueryView(viewsets.ViewSet):
    """
    我的投标信息--上传课题做关联用
    """
    authentication_classes = (ExpiringTokenAuthentication,)
    @staticmethod
    def list(request):
        # 分类（1：发展，2：监管，3：党建，4：改革，5：其他，100：全部）
        # 搜索关键字
        user = request.user
        print('my res', user)
        if user.is_active:
            data = Bid.objects.values('id', 're_title').filter(submitter=user.id, bidder_status=2).order_by('-id')
        # print(data.query)
        else:
            data = ''
        return Response(data, status=status.HTTP_200_OK)

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
            # logger.info('query_d --view.py --try_except --强转参数出错{}，--赋默认值'.format(e))
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
            data = data.filter(bidder_status__in=[1, 2, 3])
        elif tag == 'done':
            data = data.filter(conclusion_status__in=[1, 2, 3])

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


class PaticipantsQueryView(viewsets.ViewSet):
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
        par_id = self.try_except(par_id, 0)  # 验证人员id

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


class ParticipantsRcdView(viewsets.ViewSet):
    """
    研究人员按成果分类分值推荐
    """

    def list(self, request):
        num = request.query_params.get('num', 3)
        cls_t = self.request.query_params.get('cls', 100)

        cls_t = self.try_except(cls_t, 100)  # 验证类型
        num = self.try_except(num, 3)  # 验证返回数量

        if cls_t == 100:
            pro_id_queryset = Projects.objects.values('id').filter(status=1)
        else:
            pro_id_queryset = Projects.objects.values('id').filter(classify=cls_t, status=1)
        pro_id_list = [i['id'] for i in pro_id_queryset]
        # data = Relations.objects.values('pro','par', 'roles').filter(pro__in=pro_id_list)
        data = ProRelations.objects.values('par').annotate(score=Sum('score')).filter(pro__in=pro_id_list).order_by(
            '-score')[:num]
        # 根据人员id取人员名称
        res_id = [i['par'] for i in data]
        res = Participant.objects.values('name').filter(id__in=res_id)
        # print(data)

        return Response(res, status=status.HTTP_200_OK)

    @staticmethod
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/ParticipantsRcdView-list',
                         keyword='强转参数出错{}'.format(e))
            # logger.info('rcd_researcher --view.py --try_except --强转参数出错{}，--赋默认值'.format(e))
            param_key = param_default
        # print(param_key)
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


class OrgRcdView(viewsets.ViewSet):
    """
    研究机构按成果分类分值推荐
    """

    def list(self, request):
        num = request.query_params.get('num', 3)
        cls_t = self.request.query_params.get('cls', 100)

        cls_t = self.try_except(cls_t, 100)  # 验证类型
        num = self.try_except(num, 3)  # 验证返回数量

        if cls_t == 100:
            pro_id_queryset = Projects.objects.values('id').filter(status=1)
        else:
            pro_id_queryset = Projects.objects.values('id').filter(classify=cls_t, status=1)
        pro_id_list = [i['id'] for i in pro_id_queryset]
        data = ProRelations.objects.values('org').annotate(score=Sum('score')).filter(pro__in=pro_id_list,
                                                                                      org_id__isnull=False).order_by(
            '-score')[:num]
        # print(data)
        # 根据机构id取机构名称
        res_id = [i['org'] for i in data]
        res = Organization.objects.values('name').filter(id__in=res_id)
        # print(data)
        return Response(res, status=status.HTTP_200_OK)

    @staticmethod
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            set_run_info(level='error', address='/query/view.py/OrgRcdView-list',
                         keyword='强转参数出错{}'.format(e))
            # logger.info('rcd_org --view.py --try_except --强转参数出错{}，--赋默认值'.format(e))
            param_key = param_default
        # print(param_key)
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
