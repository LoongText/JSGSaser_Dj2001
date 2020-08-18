from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# 调用类常用写法
# CustomPaginator(当前页码, 每页最多能显示的页码数量, 目标数据, 每页需要显示的数量)


class CustomPaginator(Paginator):
    """
    自定义分页器
    """
    def __init__(self, current_page, per_pager_num, *args, **kwargs):
        """
        初始化自定义分页类
        :param current_page:当前页
        :param per_pager_num: 每页最多显示页码数量
        :param args: object_list, per_page, orphans=0, allow_empty_first_page=True
        :param kwargs:
        """
        self.current_page = int(current_page)
        self.per_page_num = int(per_pager_num)
        super(CustomPaginator, self).__init__(*args, **kwargs)

    def pager_num_range(self):
        """
        计算每页最多显示的页码数量
        :return:每页最多显示的页码数量
        """

        # 当前页
        # self.current_page
        # 每页最多能显示的页码数量
        # self.per_page_num
        # 总页数
        # self.num_pages

        # 总页数是django分页功能根据数据大小自动分配好的
        # 如果总页数小于每页最多能显示的页码数量
        # 那么就返回range(第一页到总页数+1),因为range取值是取(开头,结尾-1)
        if self.num_pages < self.per_page_num:
            return range(1, self.num_pages + 1)

        # 总页数特别多
        # 当你的当前页 小于或等于,最多显示的页数的一半时,显示前五个,后五个
        part = int(self.per_page_num / 2)
        if self.current_page <= part:
            return range(1, self.per_page_num + 1)

        # 极限值:如果当前页+最多显示页数一半>总页数(超出了显示的范围)
        # 返回range(总页数-最多显示的页数,总页数+1)
        if (self.current_page + part) > self.num_pages:
            return range(self.num_pages-self.per_page_num, self.num_pages + 1)

        return range(self.current_page - part, self.current_page + part + 1)


def split_page(page, per_page_num, data, per_page_count):
    """
    分页入口函数
    :param page: 当前页码
    :param per_page_num: 每页最多能显示的页码数量
    :param data: 目标数据
    :param per_page_count: 每页需要显示的数量
    :return: {获取当前页码的记录, 总记录条数, 总页数, 待显示的页码列表}
    """
    if int(page) < 1:
        page = 1
    # 调用自定义分页器
    # CustomPaginator(当前页码, 每页最多能显示的页码数量, 目标数据, 每页需要显示的数量)
    paginator = CustomPaginator(page, per_page_num, data, per_page_count)
    # 总记录条数
    item_sum = paginator.count
    # 总页数
    page_num = paginator.num_pages

    try:
        pages = paginator.page(page)  # 获取当前页码的记录
    except PageNotAnInteger:
        pages = paginator.page(1)  # 如果页码不是整数
    except EmptyPage:
        # 如果页码是一个空页  最大页
        pages = paginator.page(paginator.num_pages)
    # pre_page_num = pages.previous_page_number()
    # next_page_num = pages.next_page_number()
    # print(pre_page_num, next_page_num)
    pages_list = []
    number = int(page)
    pages_sum = int(page_num)
    # 情况1：所有页码显示在一页上
    if pages_sum < int(per_page_num):
        for i in range(pages_sum):
            pages_list.append(i+1)
    #  情况2：最后几页显示--总页数 - 当前页码 <每页显示页码数,
    elif pages_sum - number < int(per_page_num):
        for i in range(int(per_page_num)):
            pages_list.insert(0, pages_sum)
            pages_sum = pages_sum - 1
    # 情况3：中间正常显示
    else:
        for i in range(int(per_page_num)):
            pages_list.append(number)
            number = number + 1

    # print(pages_list)
    return {"pages": pages, "item_sum": item_sum, "page_num": page_num, "pages_list": pages_list, "cur_page": int(page)}


#         posts = paginator.page(current_page)
#         # has_next              是否有下一页
#         # next_page_number      下一页页码
#         # has_previous          是否有上一页
#         # previous_page_number  上一页页码
#         # object_list           分页之后的数据列表
#         # number                当前页
#         # paginator             paginator对象
# 总记录条数
# item_sum = paginator.count
# 总页数
# page_num = paginator.num_pages
# 每页显示页码数
# page_visible = paginator.pager_num_range

# print(pages.has_next()) #判断是否有下一页  true
# print(pages.has_previous())#判断是否有上一页 true
# print(pages.previous_page_number())#上一页的页码 1
# print(pages.next_page_number()) #下一页的页码 3
# print(pages.paginator.page_range) #range(1,5) 1,2,3,4
# print(pages.end_index())
