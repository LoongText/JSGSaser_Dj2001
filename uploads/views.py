from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from tables.models import Projects, Research, Participant, Organization, ProRelations, Bid
from uploads.UploadsSerializer import BaseListSerializer as Bls
from uploads.UploadsSerializer import BaseCreateSerializer as Cls
from uploads.UploadsSerializer import ProListSerializer as Pls
from uploads.UploadsSerializer import ProRetrieveSerializer as Prs
from uploads.UploadsSerializer import ProCreateSerializer as Pcs
from uploads.UploadsSerializer import ProUpdateSerializer as Pus
from uploads.UploadsSerializer import BidderCreateSerializer as Bdcs
from uploads.read_pdf import pdf2txtmanager
from jsg.settings import MEDIA_ROOT
import json
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import time
from backstage.views import add_user_behavior
# from rest_framework.decorators import authentication_classes
from login.auth import ExpiringTokenAuthentication
from login.views import set_run_info


class ResearchUploadView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    课题上传(发布招标信息)
    """
    queryset = Research.objects.all()
    authentication_classes = (ExpiringTokenAuthentication,)

    def get_serializer_class(self):
        if self.action == "list":
            return Bls
        elif self.action == 'create':
            return Cls
        else:
            return Cls

    def create(self, request, *args, **kwargs):
        # print(request.data)
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


class ProjectsUploadView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                         mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """
    成果上传
    """
    queryset = Projects.objects.all()

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
            path = '{}/{}'.format(MEDIA_ROOT, str(obj.attached))
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


@csrf_exempt
@api_view(['POST'])
# @authentication_classes([ExpiringTokenAuthentication])
def pro_update_base_info(request):
    """
    上传成果-添加基本信息
    :param request:
    :return:
    """
    # print(request.data)
    param_dict = request.data
    print(param_dict)
    re_id = param_dict.get('re_id', None),
    lead_org_list = eval(param_dict.get('lead_org'))
    research_list = eval(param_dict.get('research'))
    classify = param_dict.get('classify')
    key_word = param_dict.get('key_word')
    pro_status = param_dict.get('status')
    pro_id = param_dict.get('id', '')
    print(lead_org_list, type(lead_org_list))
    print(research_list, type(research_list))
    print(re_id, type(re_id))
    # print(pro_id, type(pro_id))
    if re_id:
        re_id = re_id[0]
    # 在成果库中修改记录
    pro_obj = Projects.objects.filter(id=pro_id)
    if pro_obj:
        pro_obj.update(
            classify=classify,
            key_word=key_word,
            bid=re_id,
            status=pro_status
        )
        # 多对多字段创建
        lead_org_list_obj = Organization.objects.filter(id__in=lead_org_list)
        research_list_obj = Organization.objects.filter(id__in=research_list)
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


@csrf_exempt
@api_view(['POST'])
# @authentication_classes([ExpiringTokenAuthentication])
def pro_update_pars(request):
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
    pro_obj = Projects.objects.filter(uuid=uuid)
    if pro_obj:
        # 保存则不变，提交则状态变化和填写发布时间
        if pro_status == 3 or pro_status == '3':
            current_date = time.strftime('%Y-%m-%d')
            pro_obj.update(release_date=current_date)

        # 根据输入的小组成员信息在人员信息和机构库中创建记录,进而在关系表中创建数据
        if par_list:
            print(par_list)
            par_list = json.loads(par_list)
            for par_dict in par_list:
                # print('----------------------', par_dict)
                unit = par_dict.get('unit', '')
                # 判断机构
                org_obj = Organization.objects.filter(name__contains=unit)
                if not org_obj:
                    # print('chuang jian org')
                    new_org_obj = Organization.objects.create(name=unit)
                    org_id = new_org_obj.id
                else:
                    org_id = org_obj[0].id

                # 判断人员
                try:
                    par_obj = Participant.objects.filter(name=par_dict['par'], unit__name=unit)
                except Exception as e:
                    # print(e)
                    set_run_info(level='error', address='/uploads/view.py/pro_update_pars',
                                 keyword='上传成果-添加课题组-找人员信息出错：{}'.format(e))
                    return Response({'res': '必须写人名'}, status=status.HTTP_404_NOT_FOUND)

                if not par_obj:
                    # print('chuang jian par')
                    unit_obj = Organization.objects.filter(name=unit)[0]
                    new_par_obj = Participant.objects.create(name=par_dict['par'], unit=unit_obj)
                    par_id = new_par_obj.id
                else:
                    par_id = par_obj[0].id

                # 在关系表中建立数据
                if par_dict['roles'] == '组长':
                    roles = 1
                    score = 1.2
                elif par_dict['roles'] == '副组长':
                    roles = 2
                    score = 1.1
                else:
                    roles = 3
                    score = 1

                pro_id = pro_obj[0].id
                relation_obj = ProRelations.objects.filter(pro_id=pro_id, par_id=par_id, org_id=org_id)

                if not relation_obj:
                    ProRelations.objects.create(roles=roles, score=score, speciality=par_dict.get('speciality', ''),
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
        return Response(status=status.HTTP_404_NOT_FOUND)


class BidderUploadView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    投标
    """
    queryset = Bid.objects.all()

    authentication_classes = (ExpiringTokenAuthentication,)

    def get_serializer_class(self):
        if self.action == 'create':
            return Bdcs

    # @requires_auth
    def create(self, request, *args, **kwargs):
        print('投标data', request.data)
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
