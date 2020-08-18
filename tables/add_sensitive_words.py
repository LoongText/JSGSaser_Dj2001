# -*- coding: UTF-8 -*-
import psycopg2
import string
import random
import datetime

# 源库
ORI_DB_HOST = '101.200.126.33'
ORI_DB_USER = 'postgres'
ORI_DB_PWD = 'postgres'
ORI_DB_NAME = 'cnki_gz'

# 目标库
TAR_DB_HOST = '101.200.126.33'
TAR_DB_USER = 'postgres'
TAR_DB_PWD = 'postgres'
TAR_DB_NAME = 'cnki_gz'


SQL_INSERT_TAR = "INSERT INTO tables_sensitivewords(id, sen_word, is_true, level) VALUES('{}', '{}',{},1)"


class MyConnect(object):
    """
    连接数据库类
    """
    def __init__(self):
        """
        初始化
        """
        self.tar_database = psycopg2.connect(
            database=ORI_DB_NAME, user=ORI_DB_USER, password=ORI_DB_PWD, host=ORI_DB_HOST, port='5432')
        self.tar_cur = self.tar_database.cursor()

        print("初始化完毕")


    def insert_data(self, value: dict):
        # 创建数据
        try:
            sql = SQL_INSERT_TAR.format(value['id'], value['sen_word'], value['is_start'])
            self.tar_cur.execute(sql)
            self.tar_database.commit()
        except Exception as e:
            self.tar_database.rollback()
            print('写数据出现异常', e)

    def __del__(self):
        print("结束")
        self.tar_database.close()


if __name__ == '__main__':
    myContent = MyConnect()
    # print(myContent.read_data())
    with open(r'C:\Users\XIAO\Desktop\反动词库.txt', 'r', encoding='gbk') as f:
        i = 245
        while True:
            line = f.readline()
            if line:
                myContent.insert_data({'id': i, 'sen_word': line.replace('\n', ''), 'is_start':True})
                i = i + 1
            else:
                break

