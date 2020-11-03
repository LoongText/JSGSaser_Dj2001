from django.test import TestCase
import time

# Create your tests here.

# current_time = time.strftime('%H%M%S')
current_date = time.strftime('%Y-%m-%d %H%M%S')


def a():
    print(current_date)
    time.sleep(3)
    print(time.strftime('%Y-%m-%d %H%M%S'))


def is_valid_date(str_date):
    '''判断是否是一个有效的日期字符串'''
    try:
        time.strptime(str_date, "%Y-%m-%d")
    except Exception:
        raise Exception("时间参数错误 near : {}".format(str_date))


if __name__ == "__main__":
    a_date = '2020/10/12'
    is_valid_date(a_date)

