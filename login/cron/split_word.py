import jieba


class SplitWord(object):
    """
    分词类
    """
    def __init__(self, stop_word_path):
        """
        :param stop_word_path: 停用词文件路径
        """
        self.stop_word_path = stop_word_path
    #     self.param_word_path = param_word_path

    def __read_stop_word(self) -> list:
        """
        读取停用词文件
        :return: 返回停用词列表
        """
        stop_word_list = []
        with open(self.stop_word_path, 'r', encoding='utf-8') as f:
            con = f.readlines()
        for i in con:
            stop_word_list.append(i[:-1])
        return stop_word_list

    def main(self, content, user_dict_path) -> list:
        """
        分词主方法
        :param content: 内容文本
        :param user_dict_path: 参照词典
        :return: 词语列表
        """
        stop_word_list = self.__read_stop_word()
        jieba.load_userdict(user_dict_path)
        res_tmp = jieba.cut(content, cut_all=False, HMM=True)
        res_list = [i for i in res_tmp if i not in stop_word_list]
        # print(res_list)
        return res_list


if __name__ == '__main__':
    a = SplitWord('./stop_word.txt')
    a.main('大理州博物馆', './userdict.txt')
