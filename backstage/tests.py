from django.test import TestCase
import os
import datetime
import time


def create_dir_not_exist(path):
    """
    判断文件夹是否存在，不存在就创建
    """
    if not os.path.exists(path):
        os.mkdir(path)


def create_dirs_not_exist(path):
    """
    判断目录是否存在,不存在就创建
    """
    if not os.path.exists(path):
        os.makedirs(path)


def create_file_not_exist(path):
    """
    判断文件是否存在,不存在就创建
    """
    if not os.path.exists(path):
        # 调用系统命令行来创建文件
        os.system(r"touch {}".format(path))


if __name__ == '__main__':
    # create_dir_not_exist(r'E:\AProject\jsg\media\2020')
    # create_dirs_not_exist(r'E:\AProject\jsg\media\2020\06\word.txt')
    # current_year = datetime.datetime.now().year
    # current_month = datetime.datetime.now().month
    # print(current_month, type(current_year))
    print(time.strftime('%H%M%S'))



