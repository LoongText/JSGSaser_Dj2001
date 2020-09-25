import time
import os


class UploadFile(object):
    def __init__(self, save_dir_path, attached):
        """
        上传文件-创建目录、验证文件名、写文件、返回最终文件名
        :param save_dir_path: 文件存储路径
        :param attached: 文件流
        """
        self.save_dir_path = save_dir_path
        self.attached = attached

    def create_dirs_not_exist(self):
        """
        判断目录是否存在,不存在就创建
        :return:
        """
        if not os.path.exists(self.save_dir_path):
            os.makedirs(self.save_dir_path)

    def file_name_is_exits(self, file_obj):
        """
        判断文件是否重名
        :param file_obj: 文件对象
        :return: 不重复的文件绝对路径
        """
        path = os.path.join(self.save_dir_path, file_obj.name)
        current_time = time.strftime('%H%M%S')
        if os.path.exists(path):
            (filename, extension) = os.path.splitext(file_obj.name)
            attached_name = '{}_{}{}'.format(filename, current_time, extension)
            path = os.path.join(self.save_dir_path, attached_name)
        else:
            attached_name = file_obj.name

        return path, attached_name

    def save_file(self, save_path):
        """
        写文件
        :param save_path: 保存文件的绝对路径（包括文件名）
        :return:
        """
        with open(save_path, 'wb') as f:
            # 在f.chunks()上循环保证大文件不会大量使用你的系统内存
            for content in self.attached.chunks():
                f.write(content)

    def handle(self):
        """
        文件处理方法
        :return: 文件名
        """
        # print('hahaha')
        self.create_dirs_not_exist()
        save_path, attached_name_fin = self.file_name_is_exits(self.attached)
        self.save_file(save_path)

        return attached_name_fin


