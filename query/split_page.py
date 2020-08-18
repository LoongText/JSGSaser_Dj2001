class SplitPages(object):

    def __init__(self, data, cur_page: int, per_page_num: int):
        """
        自定义分页
        :param data: 查询的数据对象
        :param cur_page: 当前页码
        :param per_page_num: 每页记录条数
        """
        self.data = data
        self.cur_page = cur_page
        self.per_page_num = per_page_num

    def _data_sum(self):
        return self.data.count()

    def _data_page_num(self, data_sum):
        return data_sum // self.per_page_num + 1

    def _data_list(self):
        return self.data[(self.cur_page - 1) * self.per_page_num: self.cur_page * self.per_page_num]

    def split_page(self):
        data_sum = self._data_sum()
        data_page_sum = self._data_page_num(data_sum)
        data_list = self._data_list()
        return {'sum': data_sum, 'page_num': data_page_sum, 'res': data_list}
