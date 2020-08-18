from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from tables.models import Projects, Research, ProRelations, UserDownloadBehavior, User
import os
from jsg import settings
from django.http import StreamingHttpResponse
from login.views import set_run_info
import urllib.parse


@api_view(['GET'])
# @authentication_classes([ExpiringTokenAuthentication])
def projects_download(request):
    """
    课题下载次数记录
    :param request:
    :return:
    """
    if request.method == 'GET':
        uuid = request.query_params.get('uuid', '')
        user_id = request.query_params.get('userid', 0)
        ways = request.query_params.get('d', 'v')  # 区分查看还是下载
        try:
            obj = Projects.objects.filter(uuid=uuid)[0]
            if ways == 'd':
                obj.download_num_update()  # 下载量+1
                if user_id and user_id != 'undefined' and user_id != 'null':
                    user_obj = User.objects.get(id=user_id)
                    UserDownloadBehavior.objects.create(user=user_obj, pro=obj)  # 记录下载量数据
                else:
                    UserDownloadBehavior.objects.create(pro=obj)  # 记录下载量数据
            # 显示在弹出对话框中的默认的下载文件名
            the_file_name = '{}.pdf'.format(obj.name)
            print(the_file_name)
            # download_url_fin = os.path.join(os.path.join(settings.BASE_DIR, 'static'), str(obj.attached))
            download_url_fin = os.path.join(settings.MEDIA_ROOT, str(obj.attached))
            print(download_url_fin)
            # print(content_disposition)
            # 将汉字换成ascii码，否则下载名称不能正确显示
            the_file_name = urllib.parse.quote(the_file_name)
            response = StreamingHttpResponse(file_iterator(download_url_fin))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{}"'.format(the_file_name)

            return response

            # return Response(status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/projects_download',
                         user=user_id, keyword='成果下载失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


# 读取文件
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


@api_view(['GET'])
def get_compare_status(request):
    """
    获得成果状态
    :param request:
    :return:
    """
    if request.method == 'GET':
        try:
            uuid = request.query_params.get('uuid', '')
            compare_status = Projects.objects.get(uuid=uuid).status
            return Response({"compare_status": compare_status, }, status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/get_compare_status',
                         keyword='获取成果状态失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def set_pro_status(request):
    # 成果状态设置
    if request.method == 'POST':
        try:
            print(request.data)
            param_dict = request.data
            uuid = param_dict.get('uuid', '')
            pro_status = int(param_dict.get('status', 0))
            print('set_pro_status', uuid, pro_status)
            data = Projects.objects.filter(uuid=uuid)
            if pro_status == 1:
                data.update(status=pro_status)
                ProRelations.objects.filter(pro=data[0].id).update(is_eft=True)
            else:
                data.update(status=pro_status)
                ProRelations.objects.filter(pro=data[0].id).update(is_eft=False)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/set_pro_status',
                         keyword='修改成果状态失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def set_recovery_status(request):
    # 设置成果恢复删除状态
    if request.method == 'POST':
        try:
            param_dict = request.data['data']
            # print(param_dict)
            uuid = param_dict.get('uuid', '')
            table = param_dict.get('table', 'p')
            # print(uuid, table)
            if table == 'p':
                data = Projects.objects.filter(uuid=uuid)
                res = data.update(status=1)
                ProRelations.objects.filter(pro=data[0].id).update(is_eft=True)
            else:
                res = Research.objects.filter(uuid=uuid).update(status=1)
            return Response({"res": res}, status=status.HTTP_200_OK)
        except Exception as e:
            set_run_info(level='error', address='/status_operation/view.py/set_recovery_status',
                         keyword='成果恢复删除状态失败：{}'.format(e))
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def file_list(request):
    """
    展示所有文件 home, dirs, files
    :param request:
    :return:
    """
    if request.method == 'GET':
        path = os.path.join(settings.MEDIA_ROOT, 'attached')
        files = os.walk(path)  # home, dirs, files
        return Response({"files": files}, status=status.HTTP_200_OK)
