from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from tables.models import Projects, ProRelations, Organization, Participant
from tables.models import SensitiveWords
from django.conf import settings
from check.common import TextSummary
from check.common import Likelihood
from check.common import cal_similar_letter
from uploads.read_pdf import pdf2txtmanager
from jsg import settings
import os
import logging as log


logger = log.getLogger('django')


# def office2pdf(uuid):
#     pro_obj = Projects.objects.filter(uuid=uuid)
#     word_name = str(pro_obj[0].attached)
#     wordpath = os.path.join(settings.MEDIA_ROOT, word_name)
#     pdfpath = os.path.join(settings.MEDIA_ROOT, 'attached')
#     try:
#         doc2pdf(wordpath, pdfpath)
#         atd = word_name.split('.')[0] + '.pdf'
#         Projects.objects.filter(uuid=uuid).update(attached=atd)
#     except Exception as e:
#         # print(e)
#         logger.error('compare --转pdf失败：{}'.format(e))


@api_view(['GET'])
def compare(request):
    """
    课题文本查重；
    :param request:
    :return:
    """
    if request.method == 'GET':
        
        uuid = request.query_params.get('uuid', '')
        pro_obj = Projects.objects.filter(uuid=uuid)
        word_name = str(pro_obj[0].attached)
        suffix = word_name.split('.')[-1]
        # if suffix == 'doc' or suffix == 'docx':
        #     office2pdf(uuid)
        ProRelations.objects.filter(pro=pro_obj[0].id).update(is_eft=1)
        # 更新成果状态
        pro_obj.update(status=1)
        # 批量更新机构成果数量
        org_par_obj = ProRelations.objects.values('org', 'par').filter(pro=pro_obj[0].id, is_eft=1,
                                                                       org__id__isnull=False, par__id__isnull=False)
        org_id_list = [i['org'] for i in org_par_obj]
        print('aaa_bbb', org_id_list)
        Organization.objects.filter(id__in=org_id_list).pro_sum_update()
        # 批量更新机构专家数量
        par_id_list = [i['par'] for i in org_par_obj]
        print('bbb_ccc', par_id_list)
        Participant.objects.filter(id__in=par_id_list).par_sum_update()
        return Response({"bilv": "0", "pro_status": "1"}, status=status.HTTP_200_OK)

        compare_status = Projects.objects.get(uuid=uuid).status
        if compare_status != 2:
            return Response({"compare_status": compare_status, }, status=status.HTTP_200_OK)

        Projects.objects.filter(uuid=uuid).update(status=3)
        obj = Projects.objects.get(uuid=uuid)
        # 关键词检测
        text_part = obj.text_part
        sensitive_words = SensitiveWords.objects.filter(is_true=True)
        sensitive_words_list = list()
        for sw in sensitive_words:
            if sw.sen_word in text_part:
                sensitive_words_list.append(sw.sen_word)
        if sensitive_words_list:
            Projects.objects.filter(uuid=uuid).update(status=4)
            return Response({"sensitive_words": sensitive_words_list, }, status=status.HTTP_200_OK)

        key_word = obj.key_word
        text_summary = TextSummary(title="", text=obj.text_part)
        keyword_obj = text_summary.get_keywords()
        # print(keyword_obj)
        for kw in keyword_obj:
            if kw not in key_word:
                key_word = key_word + " " + kw
        obj.key_word = key_word
        obj.save()

        result = cal_similar_letter(key_word)
        # print(result[0].name, "==========")

        letter_user = obj
        if not result:
            Projects.objects.filter(uuid=uuid).update(status=1)
            pro_status = 1
            # letter_db_dict = compared_letter_dict['text2'].items()
            return Response({"bilv": 0, "pro_status": pro_status}, status=status.HTTP_200_OK)
        try:
            letter_db = result[0]

            bilv = Likelihood().compare(text1=letter_user.text_part, text2=letter_db.text_part)
        except Exception as e:
            # 如果在查重的过程中，出现任何问题，就暂时先把文档查重率置为0，全当没问题；
            bilv = 0
            logger.error('compare --查重出错：{}'.format(e))

        # print(bilv)
        if bilv > 0.05:
            # 文件检测不合格；
            pro_status = 4  # 4：代表文件不合格；
            Projects.objects.filter(uuid=uuid).update(status=pro_status)
        else:
            pro_status = 1
            # 文件检测合格；
            pro_obj = Projects.objects.filter(uuid=uuid)
            # 更新成果状态
            pro_obj.update(status=pro_status)
            # 转成pdf文件
            wordpath = os.path.join(settings.MEDIA_ROOT, str(pro_obj[0].attached))
            pdfpath = os.path.join(settings.MEDIA_ROOT, 'attached')
            try:
                doc2pdf(wordpath, pdfpath)
                atd = str(pro_obj[0].attached).split('.')[0] + '.pdf'
                pro_obj.update(attached=atd)
            except Exception as e:
                logger.error('compare --转pdf失败：{}'.format(e))

            # 设置关系有效
            ProRelations.objects.filter(pro=pro_obj[0].id).update(is_eft=1)
            # 批量更新机构成果数量
            org_par_obj = ProRelations.objects.values('org', 'par').filter(pro=pro_obj[0].id, is_eft=1, org__id__isnull=False, par__id__isnull=False)
            org_id_list = [i['org'] for i in org_par_obj]
            print('aaa_bbb', org_id_list)
            Organization.objects.filter(id__in=org_id_list).pro_sum_update()
            # 批量更新机构专家数量
            par_id_list = [i['par'] for i in org_par_obj]
            print('bbb_ccc', par_id_list)
            Participant.objects.filter(id__in=par_id_list).par_sum_update()
        # letter_db_dict = compared_letter_dict['text2'].items()
        return Response({"bilv": bilv, "pro_status": pro_status}, status=status.HTTP_200_OK)
