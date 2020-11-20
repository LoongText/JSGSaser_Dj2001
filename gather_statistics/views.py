from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q
from query.split_page import SplitPages
from rest_framework.decorators import api_view
from login.views import set_run_info
from rest_framework.decorators import action
from collections import Counter
from collections import OrderedDict
from tables import models
import time
from query.views import permission_filter_data as pfw
from login.auth import ExpiringTokenAuthentication
import os
from query.export_data import write2excel
from django.http import StreamingHttpResponse
import urllib.parse
from jsg import settings


class NumCountView(viewsets.ViewSet):
    """
    综合统计
    """
    authentication_classes = (ExpiringTokenAuthentication,)

    def list(self, request):
        """
        启动屏综合统计
        :param request:
        :return:
        """
        # 成果总数--合格的
        pro_sum = self.get_pro_obj().count()
        # 课题招标-正在进行招标的数量
        res_sum = self.get_research_obj().count()
        # 成果浏览量
        views_sum = self.get_pro_views_obj()['views__sum']
        # 成果下载量
        download_sum = self.get_pro_downloads_obj()['downloads__sum']
        # 推进中的课题量(算小课题)
        res_ing_sum = self.get_bid_ing_obj().count()
        # 课题结题量(算小课题)
        res_ed_sum = self.get_bid_ed_obj().count()
        # 研究机构量
        org_sum = self.get_org_obj().count()
        # 研究人员量
        par_sum = self.get_par_obj().count()
        res = {'pro_sum': pro_sum, 'res_sum': res_sum, 'view_sum': views_sum, 'org_sum': org_sum,
               'download_sum': download_sum, 'res_ing_sum': res_ing_sum, 'res_ed_sum': res_ed_sum,
               'par_sum': par_sum}
        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_personal_statistics(self, request):
        """
        个人数据统计
        :param request:
        :return:
        """
        user = request.user
        # print(user)
        # 成果总数--合格的
        pro_sum = self.if_else_tmp(pfw(user, self.get_pro_obj(), 'user__org'))
        # 课题招标-正在进行招标的数量
        res_sum = self.if_else_tmp(pfw(user, self.get_research_obj(), 'user__org'))
        # 推进中的课题量(算小课题)
        res_ing_sum = self.if_else_tmp(pfw(user, self.get_bid_ing_obj(), 'submitter__org'))
        # 课题结题量(算小课题)
        res_ed_sum = self.if_else_tmp(pfw(user, self.get_bid_ed_obj(), 'submitter__org'))
        # 研究机构量
        org_sum = self.if_else_tmp(pfw(user, self.get_org_obj(), 'id'))
        # 研究人员量
        par_sum = self.if_else_tmp(pfw(user, self.get_par_obj(), 'unit'))
        # 用户总数
        user_sum = self.if_else_tmp(pfw(user, self.get_user_obj(), 'org'))

        user_daily_sum = self.get_user_daily_obj().count()

        res = {'pro_sum': pro_sum, 'res_sum': res_sum, 'res_ing_sum': res_ing_sum, 'user_sum': user_sum,
               'res_ed_sum': res_ed_sum, 'par_sum': par_sum, 'org_sum': org_sum, 'user_daily_sum': user_daily_sum}

        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_daily_login_user(self, request):
        """
        今日用户访问
        :param request:
        :return:
        """
        current_date = time.strftime('%Y-%m-%d')
        user_obj = models.UserBehavior.objects.values('user_id').filter(
            create_time__gte=current_date, user__isnull=False).distinct('user_id')
        user_obj_list = [i['user_id'] for i in user_obj]
        user_daily_obj = models.User.objects.values('username', 'first_name', 'org__name').filter(id__in=user_obj_list)
        return Response(user_daily_obj, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_daily_pro_update(self, request):
        """
        今日成果添加--以审批通过时间为准
        :param request:
        :return:
        """
        result_list = self.get_daily_pro_update_way()
        return Response(result_list, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_daily_user_register(self, request):
        """
        今日用户注册--审批通过时间为准
        :param request:
        :return:
        """
        result = self.get_daily_user_register_way()
        return Response(result, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def export_daily_pro_update(self, request):
        """
        今日成果新增导出
        :param request:
        :return:
        """
        res_obj = self.get_daily_pro_update_way()
        records = [[a['name'], a['number']] for a in res_obj]
        n = len(records)
        head_data = ['机构名称', '今日上传数量']
        download_url = os.path.join(os.path.join(os.path.join(settings.MEDIA_ROOT, 'tmp')), 'pro')
        download_url_fin = self.export_data(n, head_data, records, download_url)
        the_file_name = '数据导出.xls'

        # 将汉字换成ascii码，否则下载名称不能正确显示
        the_file_name = urllib.parse.quote(the_file_name)
        response = StreamingHttpResponse(self.file_iterator(download_url_fin))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(the_file_name)

        return response

    @action(methods=['post'], detail=False)
    def export_daily_user_register(self, request):
        """
        今日用户注册导出
        :param request:
        :return:
        """
        res_obj = self.get_daily_user_register_way()
        records = [
            [a['org__name'], a['user_daily_num'], a['user_sum']] for a in res_obj]
        n = len(records)
        head_data = ['机构名称', '今日注册数量', '注册总数']
        download_url = os.path.join(os.path.join(os.path.join(settings.MEDIA_ROOT, 'tmp')), 'user')
        download_url_fin = self.export_data(n, head_data, records, download_url)
        the_file_name = '数据导出.xls'

        # 将汉字换成ascii码，否则下载名称不能正确显示
        the_file_name = urllib.parse.quote(the_file_name)
        response = StreamingHttpResponse(self.file_iterator(download_url_fin))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(the_file_name)

        return response

    @staticmethod
    def export_data(n, head_data, records, download_url):
        """
        数据生成excel表格
        :param n:
        :param head_data:
        :param records:
        :param download_url:
        :return:
        """
        download_url_fin = write2excel(n, head_data, records, download_url)
        # print(download_url_fin)
        return download_url_fin

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
    def get_daily_pro_update_way():
        """
        今日成果添加获取方法
        :return:
        """
        current_date = time.strftime('%Y-%m-%d')
        pro_obj = models.Projects.objects.filter(approval_time=current_date, status=1)
        # print(pro_obj)
        queryset_list_fin = []
        for i in pro_obj:
            lead_org_obj = i.lead_org.all()
            research_obj = i.research.all()
            queryset_list = []
            queryset_list.extend(lead_org_obj)
            queryset_list.extend(research_obj)
            queryset_list_fin.extend(list(set(queryset_list)))
        # print(queryset_list_fin)
        queryset_list_fin_tmp = [j.name for j in queryset_list_fin]
        # print(queryset_list_fin_tmp)
        result = Counter(queryset_list_fin_tmp)
        result_list = []
        for k, v in result.items():
            # print(k, type(k))
            result_dict = {"name": k, "number": v}
            result_list.append(result_dict)
        # print(result)
        return result_list

    @staticmethod
    def get_daily_user_register_way():
        """
        今日用户添加获取方法
        :return:
        """
        current_date = time.strftime('%Y-%m-%d')
        # current_date = time.strftime('2020-07-08')
        # current_date_s = '{} 00:00:00'.format(current_date)
        # current_date_e = '{} 23:59:59'.format(current_date)
        user_obj = models.User.objects.filter(date_joined__gte=current_date, is_active=True)
        result = user_obj.values('org__id', 'org__name').annotate(user_daily_num=Count('org__id'))
        # print(result.query)
        for i in range(len(result)):
            result[i]['user_sum'] = models.User.objects.filter(org=result[i]['org__id'], is_active=True).count()

        return result

    @staticmethod
    def if_else_tmp(sum_obj):
        if sum_obj:
            # print(1)
            return sum_obj.count()
        else:
            return 0

    @staticmethod
    def get_pro_obj():
        # 成果总数--合格的
        return models.Projects.objects.filter(status=1)

    @staticmethod
    def get_pro_views_obj():
        # 成果浏览量总数
        return models.Projects.objects.aggregate(Sum('views'))

    @staticmethod
    def get_pro_downloads_obj():
        # 成果下载量总数
        return models.Projects.objects.aggregate(Sum('downloads'))

    @staticmethod
    def get_research_obj():
        # 课题招标-正在进行招标的数量
        return models.Research.objects.filter(status=1)

    @staticmethod
    def get_bid_ing_obj():
        # 推进中的课题量(算小课题)--投标中和中标
        return models.Bid.objects.filter(bidder_status__in=[1, 2], conclusion_status=0)

    @staticmethod
    def get_bid_ed_obj():
        # 课题结题量(算小课题)--审批中和已通过
        return models.Bid.objects.filter(conclusion_status__in=[1, 2])

    @staticmethod
    def get_par_obj():
        # 研究人员总数--is_show=True
        return models.Participant.objects.filter(is_show=True)

    @staticmethod
    def get_org_obj():
        # 研究机构总数--is_show=True
        return models.Organization.objects.filter(is_show=True)

    @staticmethod
    def get_user_obj():
        # 用户总数
        return models.User.objects

    @staticmethod
    def get_user_daily_obj():
        # 今日用户访问总数
        current_date = time.strftime('%Y-%m-%d')
        user_daily_obj = models.UserBehavior.objects.values('user_id').filter(
            create_time__gte=current_date, user__isnull=False).distinct('user_id')
        return user_daily_obj


@api_view(['GET'])
def get_ab_org(request):
    """
     按照机构属性分别统计有多少所属机构和人员
    :param request:
    :return:
    """
    # 用户所属组
    if request.method == 'GET':
        roles = request.query_params.get('roles', 'org')  # 统计机构还是人员 org：机构，par:人员, more:获取所有

        if roles == 'more':
            #  获取所有机构性质
            data = models.OrgNature.objects.values('id', 'remarks').order_by('ord_by')
            return Response({"data": data}, status=status.HTTP_200_OK)

        choose_role = request.query_params.get('choose_role')  # 机构性质界别：a,b
        tag = request.query_params.get('tag')  # t代表图标统计（不统计成果数为0的机构或人员）
        data = models.Organization.objects.values(
            'nature__id', 'nature__remarks', 'nature__ord_by').filter(is_show=True)
        # .exclude(nature__level=settings.ORG_NATURE_FORBIDDEN_LEVEL)

        if roles == 'org':
            if choose_role == 'a':
                data = data.filter(nature__level=settings.ORG_NATURE_HIGHER_LEVEL)
            else:
                data = data.filter(nature__level=settings.ORG_NATURE_LOWER_LEVEL)
            if tag == 't':
                data = data.exclude(pro_sum=0)
            data = data.annotate(org_num=Count('id')).order_by('nature__id')
            # print(data.query)
        else:
            data = data.filter(nature__level=settings.ORG_NATURE_LOWER_LEVEL)
            if tag == 't':
                data = data.exclude(par_sum=0)
            data = data.annotate(par_num=Sum('par_sum')).order_by('nature__id')
            # print(data.query)
        data_fin = sorted(data, key=lambda x: x['nature__ord_by'], reverse=False)
        return Response({"data": data_fin}, status=status.HTTP_200_OK)


class ProOrgCountView(viewsets.ViewSet):
    """
    成果按机构统计
    """

    def list(self, request):
        order = request.query_params.get('order', 'p')  # 排列顺序（p:成果，v:点击，r:学者）
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        keyword = request.query_params.get('kw', '')
        nature = request.query_params.get('nature', 0)
        user_id = request.query_params.get('userid', 0)
        choose_role = request.query_params.get('choose_role')  # 机构性质界别：a,b
        # tag = request.query_params.get('tag', 'org_bar')  # 区分机构列表页和统计柱状图 org_list,org_bar
        # print(request.query_params)
        # print(tag)
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

        data = models.Organization.objects.values('id', 'name', 'pro_sum', 'par_sum').filter(is_show=True).exclude(
            nature__level=settings.ORG_NATURE_FORBIDDEN_LEVEL)

        if choose_role == 'a':
            data = data.filter(nature__level=settings.ORG_NATURE_HIGHER_LEVEL)
        elif choose_role == 'b':
            data = data.filter(nature__level=settings.ORG_NATURE_LOWER_LEVEL)

        if keyword:
            # 有检索参数
            data = data.filter(name__contains=keyword)
        if nature:
            # 有机构分类
            data = data.filter(nature=nature)
        data_sum = data.count()
        for i in range(len(data)):
            org_id_list = self.get_relative_org_list(data[i]['id'])  # 获得本机构和下属机构的id
            pro_data = models.Projects.objects.values('id').filter(status=1).filter(
                Q(lead_org__id__in=org_id_list) | Q(research__id__in=org_id_list))
            pro_data_list = [i['id'] for i in pro_data]
            data[i]['pro_sum'] = len(set(pro_data_list))  # 成果总量
            # if tag == 'org_list':
            if data[i]['pro_sum'] == 0:
                data[i]['view_sum'] = 0
            else:
                data[i]['view_sum'] = pro_data.aggregate(Sum('views'))['views__sum']  # 成果总浏览量
                if data[i]['view_sum'] is None:
                    data[i]['view_sum'] = 0

        if order == 'p':
            # 成果总数排序
            data = sorted(data, key=lambda x: x['pro_sum'], reverse=True)
        elif order == 'v':
            # 根据点击量排序
            data = sorted(data, key=lambda x: x['view_sum'], reverse=True)
        else:
            # 根据学者量排序
            data = sorted(data, key=lambda x: x['par_sum'], reverse=True)

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
        return param_key

    @staticmethod
    def get_relative_org_list(ori_org_id):
        """
        获得本机构和所有下级机构
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
        return org_id_list


class ProParCountView(viewsets.ViewSet):
    """
    成果按研究人员统计
    """

    def list(self, request):
        order = request.query_params.get('order', 'p')  # 排列顺序（p:成果，t:默认创建时间，n:姓名）
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 10)
        name = request.query_params.get('name', '')
        unit = request.query_params.get('unit', '')
        nature = request.query_params.get('nature', 0)
        user_id = request.query_params.get('userid', 0)

        page = self.try_except(page, 1)  # 验证页码
        page_num = self.try_except(page_num, 10)  # 验证每页的数量

        if order not in ['p', 't', 'n']:
            order = 't'
            set_run_info(level='error', address='/gather_statistics/view.py/ParOrgCountView',
                         user=user_id, keyword='按机构统计成果-order参数传参不正确：{}'.format(order))

        org_id_list_obj = models.Organization.objects.values('id').filter(
            is_show=True, nature__level=settings.ORG_NATURE_LOWER_LEVEL)
        # .exclude(nature__level=0)

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
        # print(org_id_list_obj.query)
        org_id_list = [i['id'] for i in org_id_list_obj]

        data = models.Participant.objects.values('id', 'name', 'unit__name', 'job', 'pro_sum').filter(
            unit_id__in=org_id_list, is_show=True)
        if name:
            # 姓名检索
            data = data.filter(name__contains=name)

        if order == 't':
            data = data.order_by('-created_date')
        elif order == 'p':
            data = data.order_by('-pro_sum')
        else:
            data = data.order_by('name_pinyin')
        # print(data.query)
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
            pro_id_obj = models.Projects.objects.values('id').filter(status=1).filter(
                Q(lead_org=org_id) | Q(research=org_id)).distinct()
            # print(pro_id_obj.query)
            pro_id_list = [i['id'] for i in pro_id_obj]
        else:
            # 按人员
            pro_id_obj = models.ProRelations.objects.values('pro').filter(par=par_id, is_eft=True).distinct()
            pro_id_list = [i['pro'] for i in pro_id_obj]

        if column == 'y':
            # 根据指定类型，按年份分类统计
            if cls_t == 100:
                pro_obj = models.Projects.objects.filter(id__in=pro_id_list)
            else:
                pro_obj = models.Projects.objects.filter(classify=cls_t, id__in=pro_id_list)
            pro_obj_fin = pro_obj.values("release_date__year").annotate(year_sum=Count("id")).order_by(
                '-release_date__year')
            # print(pro_obj.query)
            res = {'res': pro_obj_fin}
        elif column == 'p':
            if org_id:
                # 按学者发布成果量统计，发布量倒序排列
                par_id_obj = models.ProRelations.objects.values('par', 'par__name').annotate(
                    pro_sum=Count('pro')).filter(org=org_id, is_eft=True, par_id__isnull=False).order_by('-pro_sum')
                res = {'res': par_id_obj}
            else:
                # 合作学者,返回指定格式
                par_id_obj = models.ProRelations.objects.values('par', 'par__name').filter(pro_id__in=pro_id_list,
                                                                                    par_id__isnull=False).distinct()
                par_id_obj_list = list(filter(lambda x: x['par'] != par_id, par_id_obj))  # 删除本身
                # print('22', par_id_obj_list)
                par_name_cur = models.Participant.objects.get(pk=par_id).name
                res = {'name': par_name_cur, 'name_id': par_id, 'res': par_id_obj_list}
        elif column == 'co':
            # 合作机构成果量
            co_org_obj = models.Projects.objects.values('lead_org', 'research').filter(status=1, id__in=pro_id_list)
            # print(co_org_obj)
            co_org_list = []
            for co_org in co_org_obj:
                if co_org['lead_org'] and co_org['lead_org'] not in co_org_list and co_org['lead_org'] != org_id:
                    co_org_list.append(co_org['lead_org'])
                if co_org['research'] and co_org['research'] not in co_org_list and co_org['research'] != org_id:
                    co_org_list.append(co_org['research'])

            # print(co_org_list)
            co_obj_list = models.Organization.objects.values('name', 'pro_sum').filter(id__in=co_org_list)
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
        pro_id_obj = models.Projects.objects.filter(status=1)

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
        re_obj = models.Research.objects.values(
            'created_date__year', 'created_date__month').exclude(created_date=None).filter(status__in=[1, 2, 3])
        bid_obj = models.Bid.objects.values(
            'bidder_date__year', 'bidder_date__month').exclude(bidder_date=None).filter(
            bidder_status__in=[1, 2, 3])
        re_obj_dict = self.list_counter(list(re_obj), 'created_date__year', 'created_date__month')
        bid_obj_dict = self.list_counter(list(bid_obj), 'bidder_date__year', 'bidder_date__month')
        year_dict = {**re_obj_dict, **bid_obj_dict}
        # print(year_dict)
        # 招标中
        re_on_obj = re_obj.filter(status=1)
        re_on_obj_dict_tmp = self.list_counter(list(re_on_obj), 'created_date__year', 'created_date__month')
        re_on_obj_dict = self.complete_dict(year_dict, re_on_obj_dict_tmp)
        # print(re_on_obj_list)
        # 推进中的课题量(算小课题)
        re_ing_obj = models.Bid.objects.values(
            'bidder_date__year', 'bidder_date__month').filter(bidder_status__in=[1, 2], conclusion_status=0)
        re_ing_obj_dict_tmp = self.list_counter(list(re_ing_obj), 'bidder_date__year', 'bidder_date__month')
        re_ing_obj_dict = self.complete_dict(year_dict, re_ing_obj_dict_tmp)
        # 已结题(算小课题)
        re_ed_obj = models.Bid.objects.values(
            'bidder_date__year', 'bidder_date__month').filter(conclusion_status__in=[1, 2])
        re_ed_obj_dict_tmp = self.list_counter(list(re_ed_obj), 'bidder_date__year', 'bidder_date__month')
        re_ed_obj_dict = self.complete_dict(year_dict, re_ed_obj_dict_tmp)
        # 投标累计数--按年份分类统计
        bid_obj_cp = bid_obj
        bid_obj_dict_tmp = self.list_counter(list(bid_obj_cp), 'bidder_date__year', 'bidder_date__month')
        bid_obj_dict = self.complete_dict(year_dict, bid_obj_dict_tmp)

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
        pro_obj_fin = models.UserClickBehavior.objects.values("create_time__year", "create_time__month").annotate(
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
        pro_obj_fin = models.UserDownloadBehavior.objects.values("create_time__year", "create_time__month").annotate(
            click_sum=Count("id"))
        # print(pro_obj_fin.query)
        # 招标中
        res = pro_obj_fin
        return Response(res, status=status.HTTP_200_OK)
