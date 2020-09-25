from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from tables.models import Projects, Research, Participant, ProRelations, Organization, Bid, OrgNature
from tables.models import UserDownloadBehavior, UserClickBehavior
from django.db.models import Sum, Count, Q
# import logging as log
from query.split_page import SplitPages
from rest_framework.decorators import api_view
from login.views import get_user_org_roles, set_run_info
from collections import Counter
from collections import OrderedDict


def get_org_roles_control(org_roles, choose_role, data):
    """
    首页-第三屏-权限控制,性质3在上边，4在下边
    :param org_roles: 用户所属机构的角色
    :param choose_role: 看出题方数据、研究方数据还是所有数据
    :param data:
    :return:
    """
    if org_roles == 'a':
        if choose_role == 'a':
            data = data.filter(nature__level__in=[3])
        elif choose_role == 'b':
            data = data.filter(nature__level__in=[4])
        else:
            data = data.exclude(nature__level__in=[0])
    else:
        data = data.filter(nature__level__in=[4])
    return data


class NumCountView(viewsets.ViewSet):
    """
    启动屏综合统计
    """

    @staticmethod
    def list(request):
        # 成果总数--合格的
        pro_sum = Projects.objects.filter(status=1).count()
        # 课题招标-正在进行招标的数量
        res_sum = Research.objects.filter(status=1).count()
        # 成果浏览量
        views_sum = Projects.objects.aggregate(Sum('views'))['views__sum']
        # 成果下载量
        download_sum = Projects.objects.aggregate(Sum('downloads'))['downloads__sum']
        # 推进中的课题量(算小课题)
        res_ing_sum = Bid.objects.filter(bidder_status__in=[1, 2], conclusion_status=0).count()
        # 课题结题量(算小课题)
        res_ed_sum = Bid.objects.filter(conclusion_status__in=[1, 2]).count()
        # 研究机构量
        org_sum = Organization.objects.count()
        # 研究人员量
        par_sum = Participant.objects.count()
        res = {'pro_sum': pro_sum, 'res_sum': res_sum, 'view_sum': views_sum, 'org_sum': org_sum,
               'download_sum': download_sum, 'res_ing_sum': res_ing_sum, 'res_ed_sum': res_ed_sum,
               'par_sum': par_sum}
        return Response(res, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_ab_org(request):
    """
     按照机构属性分别统计有多少所属机构和人员
    :param request: 甲方--可以看所有级别的；乙方--只可以看3、4级别的
    :return:
    """
    # 用户所属组
    if request.method == 'GET':
        roles = request.query_params.get('roles', 'org')  # 统计机构还是人员 org：机构，par:人员, more:获取所有

        if roles == 'more':
            #  获取所有机构性质
            data = OrgNature.objects.values('id', 'remarks').order_by('ord_by')
            return Response({"data": data}, status=status.HTTP_200_OK)

        user_id = request.query_params.get('userid', 0)
        choose_role = request.query_params.get('choose_role')  # 甲方：a,乙方：b,其他：全部数据
        tag = request.query_params.get('tag')  # t代表图标统计（不统计成果数为0的机构或人员）
        data = Organization.objects.values('nature__id', 'nature__remarks', 'nature__ord_by').filter(is_show=True)
        # print(request.query_params)
        # ---权限控制开始---
        org_roles = get_user_org_roles(user_id)
        data = get_org_roles_control(org_roles, choose_role, data)
        # ---权限控制结束---

        if roles == 'org':
            if tag == 't':
                data = data.exclude(pro_sum=0)
            data = data.annotate(org_num=Count('id')).order_by('nature__id')
            # print(data.query)
        else:
            if tag == 't':
                data = data.exclude(par_sum=0)
            data = data.exclude(is_a=True).annotate(par_num=Sum('par_sum')).order_by('nature__id')
        data_fin = sorted(data, key=lambda x: x['nature__ord_by'], reverse=False)
        return Response({"data": data_fin}, status=status.HTTP_200_OK)


class ProOrgCountView(viewsets.ViewSet):
    """
    成果按机构统计--分类甲乙方（同时属于两方时，归为甲方）
    """

    def list(self, request):
        order = request.query_params.get('order', 'p')  # 排列顺序（p:成果，v:点击，r:学者）
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        keyword = request.query_params.get('kw', '')
        nature = request.query_params.get('nature', 0)
        user_id = request.query_params.get('userid', 0)
        choose_role = request.query_params.get('choose_role')
        try:
            nature = int(nature)
        except Exception as e:
            print(e)
            nature = 0

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 10)  # 验证每页的数量
        if order not in ['p', 'v', 'r']:
            order = 'p'
            set_run_info(level='error', address='/gather_statistics/view.py/ProOrgCountView',
                         user=user_id, keyword='按机构统计成果-order参数传参不正确：{}'.format(order))

        data = Organization.objects.values('id', 'name', 'pro_sum', 'par_sum').filter(is_show=True)

        # ---权限控制开始---
        org_roles = get_user_org_roles(user_id)
        data = get_org_roles_control(org_roles, choose_role, data)
        # ---权限控制结束---

        if keyword:
            # 有检索参数
            data = data.filter(name__contains=keyword)

        if nature:
            # 有机构分类
            data = data.filter(nature=nature)

        if order == 'p':
            # 成果总数排序
            data = data.order_by('-pro_sum', '-id')
            for i in range(len(data)):
                if data[i]['pro_sum'] == 0:
                    data[i]['view_sum'] = 0
                else:
                    data[i]['view_sum'] = Projects.objects.filter(status=1).filter(
                        Q(lead_org__id=data[i]['id']) | Q(research__id=data[i]['id'])).aggregate(Sum('views'))[
                        'views__sum']  # 成果总浏览量
                    if data[i]['view_sum'] is None:
                        data[i]['view_sum'] = 0
            data_sum = data.count()
        elif order == 'v':
            # 根据点击量排序
            data_obj_list = []
            for i in range(len(data)):
                if data[i]['pro_sum'] == 0:
                    data[i]['view_sum'] = 0
                else:
                    # 成果总浏览量
                    data[i]['view_sum'] = Projects.objects.filter(status=1).filter(
                        Q(lead_org__id=data[i]['id']) | Q(research__id=data[i]['id'])).aggregate(Sum('views'))[
                        'views__sum']

                    if data[i]['view_sum'] is None:
                        data[i]['view_sum'] = 0
                data_obj_list.append(data[i])

            data = sorted(data_obj_list, key=lambda x: x['view_sum'], reverse=True)
            data_sum = len(data)
        else:
            # 根据学者量排序
            data = data.order_by('-par_sum', '-id')
            for i in range(len(data)):
                if data[i]['pro_sum'] == 0:
                    data[i]['view_sum'] = 0
                else:
                    # 成果总浏览量
                    data[i]['view_sum'] = Projects.objects.filter(status=1).filter(
                        Q(lead_org__id=data[i]['id']) | Q(research__id=data[i]['id'])).aggregate(Sum('views'))[
                        'views__sum']
                    if data[i]['view_sum'] is None:
                        data[i]['view_sum'] = 0
            data_sum = data.count()

        data_page_sum = data_sum // page_num + 1

        data_list = data[(page - 1) * page_num: page * page_num]
        res = {'sum': data_sum, 'page_num': data_page_sum, 'res': data_list}

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
            set_run_info(level='error', address='/gather_statistics/view.py/ProOrgCountView',
                         keyword='按机构统计成果-参数强转失败：{}'.format(e))
            # logger.info('org_count --view.py --try_except --强转参数出错{}，--赋默认值'.format(e))
        return param_key


class ProParCountView(viewsets.ViewSet):
    """
    成果按研究人员统计--只统计乙方人员
    """

    def list(self, request):
        order = request.query_params.get('order', 'p')  # 排列顺序（p:成果，t:默认创建时间，n:姓名）
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        name = request.query_params.get('name', '')
        unit = request.query_params.get('unit', '')
        nature = request.query_params.get('nature', 0)
        user_id = request.query_params.get('userid', 0)
        # choose_role = request.query_params.get('choose_role')
        choose_role = 'b'

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 10)  # 验证每页的数量

        if order not in ['p', 't', 'n']:
            order = 't'
            set_run_info(level='error', address='/gather_statistics/view.py/ParOrgCountView',
                         user=user_id, keyword='按机构统计成果-order参数传参不正确：{}'.format(order))

        org_id_list_obj = Organization.objects.values('id').filter(is_show=True).exclude(is_a=True)

        #  ---控制权限开始---
        org_roles = get_user_org_roles(user_id)
        org_id_list_obj = get_org_roles_control(org_roles, choose_role, org_id_list_obj)

        #  ---控制权限结束---

        if unit:
            # 机构检索
            org_id_list_obj = org_id_list_obj.filter(name__contains=unit)
        try:
            nature = int(nature)
        except Exception as e:
            print(e)
            nature = 0
        if nature:
            # 机构分类
            org_id_list_obj = org_id_list_obj.filter(nature=nature)

        org_id_list = [i['id'] for i in org_id_list_obj]

        data = Participant.objects.values('id', 'name', 'unit__name', 'job', 'pro_sum').filter(
            unit_id__in=org_id_list)
        if name:
            # 姓名检索
            data = data.filter(name__contains=name)

        if order == 't':
            data = data.order_by('-created_date')
        elif order == 'p':
            data = data.order_by('-pro_sum')
        else:
            data = data.order_by('name_pinyin')
        # print(data)
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
            set_run_info(level='error', address='/gather_statistics/view.py/ParOrgCountView',
                         keyword='按机构统计成果-强转参数失败：{}'.format(e))
            # logger.info('par_count --view.py --try_except --强转参数出错{}，--赋默认值'.format(e))
        return param_key


class ProjectsStatisticsView(viewsets.ViewSet):
    """
    机构或人员详情页-成果定向统计分析
    """

    def list(self, request):
        # 成果分类（1：发展，2：监管，3：党建，4：改革，5：其他，100：全部）
        cls_t = request.query_params.get('cls', 100)
        org_id = request.query_params.get('org_id', 0)
        column = request.query_params.get('column', 'y')  # 默认按年份统计
        par_id = request.query_params.get('par_id', 0)

        cls_t = self.try_except(cls_t, 100)  # 验证分类
        org_id = self.try_except(org_id, 0)  # 验证机构id
        par_id = self.try_except(par_id, 0)  # 验证人员id

        # 找出所有的成果id
        if org_id:
            # 按机构
            # pro_id_obj = ProRelations.objects.values('pro').filter(org=org_id, is_eft=True).distinct()
            pro_id_obj = Projects.objects.values('id').filter(status=1).filter(Q(lead_org=org_id) | Q(research=org_id)).distinct()
            # print(pro_id_obj.query)
            pro_id_list = [i['id'] for i in pro_id_obj]
        else:
            # 按人员
            pro_id_obj = ProRelations.objects.values('pro').filter(par=par_id, is_eft=True).distinct()
            pro_id_list = [i['pro'] for i in pro_id_obj]

        if column == 'y':
            # 根据指定类型，按年份分类统计
            if cls_t == 100:
                pro_obj = Projects.objects.filter(id__in=pro_id_list)
            else:
                pro_obj = Projects.objects.filter(classify=cls_t, id__in=pro_id_list)
            pro_obj_fin = pro_obj.values("release_date__year").annotate(year_sum=Count("id")).order_by(
                '-release_date__year')
            # print(pro_obj.query)
            res = {'res': pro_obj_fin}
        elif column == 'p':
            if org_id:
                # 按学者发布成果量统计，发布量倒序排列
                par_id_obj = ProRelations.objects.values('par', 'par__name').annotate(
                    pro_sum=Count('pro')).filter(org=org_id, is_eft=True, par_id__isnull=False).order_by('-pro_sum')
                res = {'res': par_id_obj}
            else:
                # 合作学者,返回指定格式
                par_id_obj = ProRelations.objects.values('par', 'par__name').filter(pro_id__in=pro_id_list,
                                                                                    par_id__isnull=False).distinct()
                par_id_obj_list = list(filter(lambda x: x['par'] != par_id, par_id_obj))  # 删除本身
                # print('22', par_id_obj_list)
                par_name_cur = Participant.objects.get(pk=par_id).name
                res = {'name': par_name_cur, 'name_id': par_id, 'res': par_id_obj_list}
        elif column == 'co':
            # 合作机构成果量
            co_org_obj = Projects.objects.values('lead_org', 'research').filter(status=1, id__in=pro_id_list)
            # print(co_org_obj)
            co_org_list = []
            for co_org in co_org_obj:
                if co_org['lead_org'] and co_org['lead_org'] not in co_org_list and co_org['lead_org'] != org_id:
                    co_org_list.append(co_org['lead_org'])
                if co_org['research'] and co_org['research'] not in co_org_list and co_org['research'] != org_id:
                    co_org_list.append(co_org['research'])

            # print(co_org_list)
            co_obj_list = Organization.objects.values('name', 'pro_sum').filter(id__in=co_org_list)
            res = {'res': co_obj_list}
        else:
            res = {'res': ['参数错误']}
        return Response(res, status=status.HTTP_200_OK)

    @staticmethod
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            set_run_info(level='error', address='/gather_statistics/view.py/ProjectsStatisticsView',
                         keyword='强转参数失败：{}'.format(e))
            param_key = param_default
        # print(param_key)
        return param_key


class ProjectsStatisticsYearView(viewsets.ViewSet):
    """
    成果定向统计分析--综合统计页面--按年份和类型返回成果对应数量
    """

    def list(self, request):
        # 成果分类（1：发展，2：监管，3：党建，4：改革，5：其他，100：全部）
        cls_t = request.query_params.get('cls', 100)
        cls_t = self.try_except(cls_t, 100)  # 验证分类

        # 找出所有的成果id
        pro_id_obj = Projects.objects.filter(status=1)

        # 根据指定类型，按年份分类统计
        if cls_t == 100:
            pass
        else:
            pro_id_obj = pro_id_obj.filter(classify=cls_t)
        pro_obj_fin = pro_id_obj.values("release_date__year").annotate(year_sum=Count("id")).filter(
            release_date__year__isnull=False).order_by('-release_date__year')
        # print(pro_obj.query)
        res = {'res': pro_obj_fin}
        return Response(res, status=status.HTTP_200_OK)

    @staticmethod
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            set_run_info(level='error', address='/gather_statistics/view.py/ProjectsStatisticsYearView',
                         keyword='强转参数失败：{}'.format(e))
            param_key = param_default
        # print(param_key)
        return param_key


class ResearchStatisticsYearView(viewsets.ViewSet):
    """
    课题定向统计分析--综合统计页面多线表--按年份和类型返回课题对应数量
    """

    def list(self, request):
        """
        # 返回不同状态下的课题按照月份统计结果
        # 要求： 所有返回数据的数量要相同，不同的用0补齐
        # 课题状态（(0, '未开启'), (1, '招标中'), (2, '推进中'), (3, '已结题'), (4, '删除')）
        :param request:
        :return:
        """

        # 获取所有年份， 作为补齐数据的参照
        re_obj = Research.objects.values(
            'created_date__year', 'created_date__month').exclude(created_date=None).filter(status__in=[1, 2, 3])
        re_obj_dict = self.list_counter(list(re_obj), 'created_date__year', 'created_date__month')
        # print(re_obj_dict)
        # 招标中
        re_on_obj = re_obj
        re_on_obj_dict_tmp = self.list_counter(list(re_on_obj), 'created_date__year', 'created_date__month')
        re_on_obj_dict = self.complete_dict(re_obj_dict, re_on_obj_dict_tmp)
        # print(re_on_obj_list)
        # 推进中
        re_ing_obj = re_obj.filter(status=2)
        re_ing_obj_dict_tmp = self.list_counter(list(re_ing_obj), 'created_date__year', 'created_date__month')
        re_ing_obj_dict = self.complete_dict(re_obj_dict, re_ing_obj_dict_tmp)
        # 已结题
        re_ed_obj = re_obj.filter(status=3)
        re_ed_obj_dict_tmp = self.list_counter(list(re_ed_obj), 'created_date__year', 'created_date__month')
        re_ed_obj_dict = self.complete_dict(re_obj_dict, re_ed_obj_dict_tmp)
        # 投标累计数--按年份分类统计
        bid_obj = Bid.objects.values(
            'bidder_date__year', 'bidder_date__month').filter(bidder_status__in=[1, 2, 3],
                                                              bidding__status__in=[1, 2, 3])
        bid_obj_dict_tmp = self.list_counter(list(bid_obj), 'bidder_date__year', 'bidder_date__month')
        bid_obj_dict = self.complete_dict(re_obj_dict, bid_obj_dict_tmp)

        res = {'re_on_obj': re_on_obj_dict, 're_ing_obj': re_ing_obj_dict, 're_ed_obj': re_ed_obj_dict,
               'bid_obj': bid_obj_dict}
        return Response(res, status=status.HTTP_200_OK)

    @staticmethod
    def list_counter(list_obj, param1, param2):
        """
        分组统计查询结果
        :param list_obj: 查询结果
                        [{'bidder_date__year': 2020, 'bidder_date__month': 7},
                        {'bidder_date__year': 2020, 'bidder_date__month': 7}]
        :param param1: 查询结果的每个子集字典中键值1(bidder_date__year)
        :param param2: 查询结果的每个子集字典中键值2(bidder_date__month)
        :return: Counter({(2020, 7): 5, (2020, 8): 2})
        """
        list_obj_fin = []
        for dict_obj in list(list_obj):
            list_obj_fin.append((dict_obj[param1], dict_obj[param2]))
        # Counter中的二级对象不能是字典， 所以将其转化为数组
        result = Counter(list_obj_fin)
        result_dict = {}
        for k, v in result.items():
            # print(k, type(k))
            result_dict['{}-{}'.format(k[0], k[1])] = v
        # print(result)
        return result_dict

    @staticmethod
    def complete_dict(big_range_dict, small_range_dict):
        """
        将字典补齐，差值用0补齐，然后排序，用集合的方法
        :param big_range_dict: 参照物字典
        :param small_range_dict: 目标对象字典
        :return: OrderedDict([('2020-7', 5), ('2020-8', 2)])
        """
        mid_range_set = big_range_dict.keys() - small_range_dict.keys()
        for j in mid_range_set:
            small_range_dict.update({j: 0})
        # 排序，字典是无序的OrderedDict有
        result_dict = OrderedDict(sorted(small_range_dict.items(), key=lambda t: t[0]))
        return result_dict


class UserClickStsView(viewsets.ViewSet):
    """
    用户点击成果按月份统计
    """

    @staticmethod
    def list(request):
        # 获取所有年份
        pro_obj_fin = UserClickBehavior.objects.values("create_time__year", "create_time__month").annotate(
            click_sum=Count("id"))
        # print(pro_obj_fin.query)
        res = sorted(pro_obj_fin, key=lambda x: x['create_time__year'] + x['create_time__month'], reverse=False)
        # print(res)
        return Response(res, status=status.HTTP_200_OK)


class UserDownloadStsView(viewsets.ViewSet):
    """
    用户下载成果按月份统计
    """

    @staticmethod
    def list(request):
        # 获取所有年份
        pro_obj_fin = UserDownloadBehavior.objects.values("create_time__year", "create_time__month").annotate(
            click_sum=Count("id"))
        # print(pro_obj_fin.query)
        # 招标中
        res = pro_obj_fin
        return Response(res, status=status.HTTP_200_OK)
