# -*- coding: UTF-8 -*-
import psycopg2
from pypinyin import lazy_pinyin

# 源库
ORI_DB_HOST = '101.200.126.33'
ORI_DB_USER = 'postgres'
ORI_DB_PWD = 'postgres'
ORI_DB_NAME = 'cnki_gz_dev'

# 目标库
TAR_DB_HOST = '101.200.126.33'
TAR_DB_USER = 'postgres'
TAR_DB_PWD = 'postgres'
TAR_DB_NAME = 'cnki_gz_dev'


SQL_SELECT_ORI = 'SELECT id,name FROM tables_participant'
# SQL_SELECT_TAR = 'SELECT id,textpart FROM "BasicData"'
SQL_UPDATE_TAR = "UPDATE tables_participant set name_pinyin='{}' where id={}"


class MyConnect(object):
    """
    连接数据库类
    """
    def __init__(self):
        """
        初始化
        """
        self.ori_database = psycopg2.connect(
            database=ORI_DB_NAME, user=ORI_DB_USER, password=ORI_DB_PWD, host=ORI_DB_HOST, port='5432')
        self.ori_cur = self.ori_database.cursor()
        self.tar_database = psycopg2.connect(
            database=ORI_DB_NAME, user=ORI_DB_USER, password=ORI_DB_PWD, host=ORI_DB_HOST, port='5432')
        self.tar_cur = self.tar_database.cursor()

        print("初始化完毕")

    def read_data(self):
        # 读数据
        try:
            sql = SQL_SELECT_ORI
            self.ori_cur.execute(sql)
            self.ori_database.commit()
            data = self.ori_cur.fetchall()
            return data
        except Exception as e:
            self.ori_database.rollback()
            print("读数据出现异常", e)

    def update_data(self, value: dict):
        # 更新数据
        try:
            # print("开始更新数据")
            name_pinyin = ''.join(lazy_pinyin(value['name']))

            sql = SQL_UPDATE_TAR.format(name_pinyin, value['id'])
            self.tar_cur.execute(sql)
            self.tar_database.commit()
        except Exception as e:
            self.tar_database.rollback()
            print('写数据出现异常', e)

    def __del__(self):
        print("结束")
        self.ori_database.close()
        self.tar_database.close()


if __name__ == '__main__':
    myContent = MyConnect()
    # print(myContent.read_data())
    content = myContent.read_data()
    for i in content:
        print(i[0])
        myContent.update_data({'id': i[0], 'name': i[1]})
