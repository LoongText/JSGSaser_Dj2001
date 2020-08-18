from jsg.settings import STOP_WORD_PATH
from tables.models import HotWords, UserBehavior
from login.cron import split_word
import datetime
import os
import time



def create_hotword():
    """
    生成热词记录
    """
    # 1.首先将用户行为数据打散变成词语,存入列表
    keyword_split_list = []
    cur_date = datetime.datetime.now().date()  # 当前日期格式
    # yester_day = cur_date - datetime.timedelta(days=1)  # 前一天日期
    pre_week = cur_date - datetime.timedelta(weeks=1)  # 前一周日期
    # 查询前一周数据,也可以用range,我用的是glt,lte大于等于
    # print(cur_date, pre_week)
    keyword_query_set = UserBehavior.objects.values('keyword').filter(create_time__gte=pre_week, create_time__lte=cur_date)
    # print(keyword_query_set.query)
    print(keyword_query_set)

    for i_dict in keyword_query_set:
        split_obj = split_word.SplitWord(STOP_WORD_PATH + '/cron/stop_word.txt')
        i_list = split_obj.main(i_dict['keyword'], STOP_WORD_PATH + '/cron/userdict.txt')
        keyword_split_list.extend(i_list)
    # res_list = [i for i in keyword_split_list if i not in stop_word_list]  # 去除停用词
    # print(keyword_split_list)
    # print(res_list)
    res_dict = dict(Counter(keyword_split_list))
    print(res_dict)
    insert_db_list = []
    for key, value in res_dict.items():
        obj = HotWords(hot_word=key, num=value, is_true=True)
        insert_db_list.append(obj)

    HotWords.objects.bulk_create(insert_db_list)