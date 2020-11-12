from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from tables import models
from uploads.UploadsSerializer import BaseListSerializer as Bls
from uploads.UploadsSerializer import BaseCreateSerializer as Cls
from uploads.UploadsSerializer import BaseUpdateSerializer as Uls
from uploads.UploadsSerializer import ProListSerializer as Pls
from uploads.UploadsSerializer import ProRetrieveSerializer as Prs
from uploads.UploadsSerializer import ProCreateSerializer as Pcs
from uploads.UploadsSerializer import ProUpdateSerializer as Pus
from uploads.UploadsSerializer import BidderListSerializer as Bdls
from uploads.UploadsSerializer import BidderCreateSerializer as Bdcs
from uploads.UploadsSerializer import BidderUpdateSerializer as Bdus
from uploads.UploadsSerializer import BidderRetirveSerializer as Bdrs
from uploads.UploadsSerializer import OrgCreateSerializer as Ocs
from uploads.UploadsSerializer import OrgRetriveSerializer as Ors
from uploads.UploadsSerializer import OrgUpdateSerializer as Ous
from uploads.UploadsSerializer import ParCreateSerializer as Par_cs
from uploads.UploadsSerializer import ParRetriveSerializer as Par_rs
from uploads.UploadsSerializer import ParUpdateSerializer as Par_us
# from uploads.UploadsSerializer import NewsTextListSerializer as New_t
# from uploads.UploadsSerializer import NewsImageListSerializer as New_i
from uploads.UploadsSerializer import NewsTextList2Serializer as New_ti
from uploads.UploadsSerializer import NewsCreateSerializer as New_c
from uploads.UploadsSerializer import NewsUpdateSerializer as New_u
from uploads.UploadsSerializer import NewsCreateSerializer as New_r
from login.auth import ExpiringTokenAuthentication
from login.views import add_user_behavior
from uploads.read_pdf import pdf2txtmanager
import json
from jsg import settings
from rest_framework.decorators import action
from django.db.models import Q
from query.split_page import SplitPages
from django.http import StreamingHttpResponse
from login.views import set_run_info
import urllib.parse
import os


class ResearchUploadView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    """
    课题上传(发布招标信息)
    """
    queryset = models.Research.objects.all()
    authentication_classes = (ExpiringTokenAuthentication,)

    def get_serializer_class(self):
        if self.action == "list":
            return Bls
        elif self.action == 'create':
            return Cls
        elif self.action == 'update':
            return Uls
        else:
            return Cls

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='上传课题信息：{}'.format(obj.id), user_obj=request.user)
        # -- 记录结束 --
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        obj = serializer.save()
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        print(request.data)
        # print(serializer.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ProjectsUploadView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                         mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """
    成果上传
    """
    queryset = models.Projects.objects.all()

    # authentication_classes = (ExpiringTokenAuthentication,)

    def get_serializer_class(self):
        if self.action == 'list':
            return Pls
        elif self.action == 'create':
            return Pcs
        elif self.action == 'update':
            return Pus
        else:
            return Prs

    # @requires_auth
    def create(self, request, *args, **kwargs):
        print('成果data', request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        if obj.attached:
            path = '{}/{}'.format(settings.MEDIA_ROOT, str(obj.attached))
            try:
                content = self.read_con(path)
                obj.text_part = content
                obj.save()
            except Exception as e:
                print('读取文件出错：', e)
            headers = self.get_success_headers(serializer.data)
            # if request.data.get('user') and request.data.get('user') != 'undefined':
            #     # -- 记录开始 --
            #     add_user_behavior(keyword='', search_con='上传成果信息-1：{}'.format(obj.id),
            #     user_obj=request.data.get('user'))
            #     # -- 记录结束 --
            # else:
            #     add_user_behavior(keyword='', search_con='上传成果信息-1：{}'.format(obj.id))
            return Response({'uuid': obj.uuid, 'id': obj.id}, status=status.HTTP_201_CREATED, headers=headers)
        else:
            headers = self.get_success_headers(serializer.data)
            return Response(status=status.HTTP_403_FORBIDDEN, headers=headers)

    def perform_create(self, serializer):
        obj = serializer.save()
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        param_dict = {'re_id': request.data.get('re_id'),
                      'lead_org': eval(request.data.get('lead_org')),
                      'research': eval(request.data.get('research')),
                      'classify': request.data.get('classify'),
                      'key_word': request.data.get('key_word'),
                      'status': request.data.get('status')}
        serializer = self.get_serializer(instance, data=param_dict, partial=partial)
        # print(request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='上传成果信息-2：{}'.format(instance.id), user_obj=request.user)
        # -- 记录结束 --
        return Response(serializer.data)

    @staticmethod
    def read_con(path):
        """
        读取pdf文件
        :param path:
        :return:
        """
        content = ''
        try:
            content = pdf2txtmanager.pdf2text(path)
        except Exception as e:
            set_run_info(level='error', address='/uploads/view.py/ProjectsUploadView-read_con',
                         keyword='读取pdf文件失败：{}'.format(e))
        return content

    @action(methods=['POST'], detail=False)
    def pro_update_base_info(self, request):
        """
        上传成果-添加基本信息
        :param request:
        :return:
        """
        # print(request.data)
        param_dict = request.data
        # print(param_dict)
        re_id = param_dict.get('re_id', None),
        lead_org_list = eval(param_dict.get('lead_org'))
        research_list = eval(param_dict.get('research'))
        classify = param_dict.get('classify')
        key_word = param_dict.get('key_word')
        pro_status = param_dict.get('status')
        pro_id = param_dict.get('id', '')
        abstract = param_dict.get('abstract', '')
        # print(lead_org_list, type(lead_org_list))
        # print(research_list, type(research_list))
        # print(re_id, type(re_id))
        # print(pro_id, type(pro_id))
        if re_id:
            re_id = re_id[0]
        # 在成果库中修改记录
        pro_obj = models.Projects.objects.filter(id=pro_id)
        if pro_obj:
            pro_obj.update(
                classify=classify,
                key_word=key_word,
                bid=re_id,
                status=pro_status,
                abstract=abstract
            )
            # 多对多字段创建
            lead_org_list_obj = models.Organization.objects.filter(id__in=lead_org_list)
            research_list_obj = models.Organization.objects.filter(id__in=research_list)
            pro_obj[0].lead_org.add(*lead_org_list_obj)
            pro_obj[0].research.add(*research_list_obj)
            # # -- 记录开始 --
            # if request.user.is_active:
            #     add_user_behavior(keyword='', search_con='上传成果信息-2：{}'.format(pro_id), user_obj=request.user)
            # else:
            #     add_user_behavior(keyword='', search_con='上传成果信息-2：{}'.format(pro_id))
            # # -- 记录结束 --
            return Response(status=status.HTTP_200_OK)
        else:
            set_run_info(level='error', address='/uploads/view.py/pro_update_base_info',
                         keyword='上传成果-添加基本信息-未找到成果信息')
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['POST'], detail=False)
    def pro_update_pars(self, request):
        """
        添加课题组
        :param request:
        :return:
        """
        # print(request.data)
        param_dict = request.data
        print(param_dict)
        uuid = param_dict.get('uuid', '')
        pro_status = param_dict.get('status', 2)
        par_list = param_dict.get('par_list', [])

        # 在成果库中修改记录
        pro_obj = models.Projects.objects.filter(uuid=uuid)
        if pro_obj:
            # 保存则不变，提交则状态变化和填写发布时间
            # if pro_status == 3 or pro_status == '3':
            #     current_date = time.strftime('%Y-%m-%d')
            #     pro_obj.update(release_date=current_date)

            # 根据输入的小组成员信息在人员信息和机构库中创建记录,进而在关系表中创建数据
            if par_list:
                # print(par_list)
                par_list = json.loads(par_list)
                for par_dict in par_list:
                    # print('----------------------', par_dict)
                    unit = par_dict.get('org__name', '')
                    par_name = par_dict.get('par__name', '')
                    # 判断机构
                    org_obj = models.Organization.objects.filter(name__contains=unit)
                    if not org_obj:
                        # print('chuang jian org')
                        new_org_obj = models.Organization.objects.create(name=unit)
                        org_id = new_org_obj.id
                    else:
                        org_id = org_obj[0].id

                    # 判断人员
                    try:
                        par_obj = models.Participant.objects.filter(name=par_name, unit__name=unit)
                    except Exception as e:
                        # print(e)
                        set_run_info(level='error', address='/uploads/view.py/pro_update_pars',
                                     keyword='上传成果-添加课题组-找人员信息出错：{}'.format(e))
                        return Response({'res': '必须写人名'}, status=status.HTTP_404_NOT_FOUND)

                    if not par_obj:
                        # print('chuang jian par')
                        unit_obj = models.Organization.objects.filter(name=unit)[0]
                        new_par_obj = models.Participant.objects.create(name=par_name, unit=unit_obj)
                        par_id = new_par_obj.id
                    else:
                        par_id = par_obj[0].id

                    # 在关系表中建立数据
                    # roles = settings.ROLES_NAME[par_dict['roles']]
                    roles = par_dict['roles']
                    score = settings.ROLES_SCORE[roles]
                    pro_id = pro_obj[0].id
                    relation_obj = models.ProRelations.objects.filter(pro_id=pro_id, par_id=par_id, org_id=org_id)

                    if not relation_obj:
                        models.ProRelations.objects.create(roles=roles, score=score, speciality=par_dict.get('speciality', ''),
                                                    job=par_dict.get('job', ''), task=par_dict.get('task', ''),
                                                    pro_id=pro_id, par_id=par_id, org_id=org_id, is_eft=False)
                    else:
                        pass
                # # -- 记录开始 --
                # if request.user.is_active:
                #     add_user_behavior(keyword='',
                #     search_con='上传成果信息-3：{},{}'.format(uuid, pro_status), user_obj=request.user)
                # else:
                #     add_user_behavior(keyword='', search_con='上传成果信息-3：{},{}'.format(uuid, pro_status))
                # # -- 记录结束 --
                return Response(status=status.HTTP_200_OK)
            else:
                # 没有添加小组成员
                return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class BidderUploadView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                       mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """
    投标
    """
    queryset = models.Bid.objects.all()

    authentication_classes = (ExpiringTokenAuthentication,)

    def get_serializer_class(self):
        if self.action == 'create':
            return Bdcs
        elif self.action == 'update':
            return Bdus
        elif self.action == 'list':
            return Bdls
        else:
            return Bdrs

    def create(self, request, *args, **kwargs):
        # print('投标data', request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='投标：{}'.format(obj.id), user_obj=request.user)
        # -- 记录结束 --
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        obj = serializer.save()
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        print('bid_update', request.data)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class OrgManageView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin):
    """
    机构管理
    """
    queryset = models.Organization.objects.all()

    authentication_classes = (ExpiringTokenAuthentication,)

    def get_serializer_class(self):
        if self.action == 'create':
            return Ocs
        elif self.action == 'update':
            return Ous
        else:
            return Ors

    def create(self, request, *args, **kwargs):
        print(request.data)
        # print('--------------------- ')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        # print(serializer.data)
        headers = self.get_success_headers(serializer.data)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='创建机构：{}'.format(obj.id), user_obj=request.user)
        # -- 记录结束 --
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        obj = serializer.save()
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ParManageView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin):
    """
    人员管理
    """
    queryset = models.Participant.objects.all()

    authentication_classes = (ExpiringTokenAuthentication,)

    def get_serializer_class(self):
        if self.action == 'create':
            return Par_cs
        elif self.action == 'update':
            return Par_us
        # elif self.action == 'list':
        #     return Par_ls
        else:
            return Par_rs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # -- 记录开始 --
        add_user_behavior(keyword='', search_con='创建人员：{}'.format(obj.id), user_obj=request.user)
        # -- 记录结束 --
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        obj = serializer.save()
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class NewsManageView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin, mixins.ListModelMixin):
    """
    新闻管理--平台管理员和超管专属
    """
    queryset = models.News.objects.filter(is_show=True)

    authentication_classes = (ExpiringTokenAuthentication,)

    def get_serializer_class(self):
        """必须要完整，否则为报错NoneType"""
        if self.action == 'create':
            return New_c
        elif self.action == 'update':
            return New_u
        else:
            return New_r

    @action(methods=['GET'], detail=False)
    def get_news_list(self, request):
        """
        获得新闻列表
        :return:
        """
        page = request.query_params.get('page', 1)
        page_num = request.query_params.get('page_num', 5)
        keyword = request.query_params.get('kw', '')
        tag = request.query_params.get('tag', 't')  # t:正文 i:图片 ti:没有图片的正文

        page = self.try_except(page, 1)  # 验证类型
        page_num = self.try_except(page_num, 10)  # 验证返回数量

        if tag == 't':
            data = NewsManageView.queryset.values('id', 'title', 'text_create_time', 'text_attached').order_by('-text_create_time')
        elif tag == 'i':
            data = NewsManageView.queryset.values('id', 'title', 'image_attached', 'text_create_time').filter(image_attached__isnull=False).exclude(image_attached='').order_by('-text_create_time')
        else:
            # 没有图片的正文，返回全部
            data = NewsManageView.queryset.filter(Q(image_attached__isnull=True) | Q(image_attached='')).order_by('-id')
            res = New_ti(instance=data, many=True)
            return Response(res.data, status=status.HTTP_200_OK)
        if keyword:
            data = data.filter(title__contains=keyword)

            # -- 记录开始 --
            add_user_behavior(keyword=keyword, search_con='搜索新闻信息', user_obj=request.user)
            # -- 记录结束 --

        sp = SplitPages(data, page, page_num)
        res = sp.split_page()
        return Response(res, status=status.HTTP_200_OK)

    @action(methods=['PUT'], detail=True)
    def set_news_status(self, request, pk):
        """
        设置新闻不可见
        :return:
        """
        try:
            models.News.objects.filter(id=pk).update(is_show=False)
            add_user_behavior(keyword='', search_con='设置新闻不可见({})'.format(pk), user_obj=request.user)
        except Exception as e:
            set_run_info(level='error', address='/uploads/view.py/NewsManageView-set_news_status',
                         keyword='设置新闻不可见失败：{}'.format(e))
        return Response(status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def get_news_file(self, request, pk):
        """
        查看新闻正文pdf
        :param request:
        :param pk:
        :return:
        """
        try:
            obj = models.News.objects.get(id=pk)
            # the_file_name = '{}.pdf'.format(obj.title)
            the_file_name = str(obj.text_attached).split('/')[-1]
            print(the_file_name)
            download_url_fin = os.path.join(settings.MEDIA_ROOT, str(obj.text_attached))
            print(download_url_fin)
            # print(content_disposition)
            # 将汉字换成ascii码，否则下载名称不能正确显示
            the_file_name = urllib.parse.quote(the_file_name)
            response = StreamingHttpResponse(self.file_iterator(download_url_fin))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(the_file_name)

            return response
        except Exception as e:
            set_run_info(level='error', address='/uploads/view.py/NewsManageView-get_news_file',
                         keyword='查看新闻正文pdf失败：{}'.format(e))
            return Response({'msg': "查看新闻正文pdf失败", "status": 404}, status=status.HTTP_200_OK)

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
    def try_except(param_key, param_default):
        # 判断参数是否可以被是否是数字，不是的话，强转，强转不成功或者是负数，置为默认值
        try:
            param_key = int(param_key)
            if param_key < 1:
                param_key = param_default
        except Exception as e:
            set_run_info(level='error', address='/upload/view.py/NewsManageView',
                         keyword='强转参数出错{}'.format(e))
            param_key = param_default
        return param_key
