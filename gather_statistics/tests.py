from django.test import TestCase

# Create your tests here.
re_obj_dict = {'2020-8': 9, '2020-9': 2, '2020-7': 3}
bid_obj_dict = {'2020-8': 1, '2020-9': 1, '2020-7': 1, '2020-10': 1}
# mid_range_set = re_obj_dict.keys() - bid_obj_dict.keys()
mid_range_set = {**bid_obj_dict, **re_obj_dict}
print(mid_range_set)
# print(len(bid_obj_dict))
