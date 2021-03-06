from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from query.views import *
from uploads.views import *
from login.views import *
from gather_statistics.views import *
from check.views import *
from status_operation.views import *
from evaluate_bid.views import *
from django.urls import re_path
from django.views.static import serve

router = routers.DefaultRouter()
# 成果检索
router.register(r'query', ProjectsQueryView, basename='query')
# 我的成果检索/修改/详情
router.register(r'pro', ProjectsManageView, basename='pro')
# 成果审批
router.register(r'sp_query', SPProjectsQueryView, basename='sp_query')
# 优秀成果管理
router.register(r'good_pro_manage', GoodProjectsManageView, basename='good_pro_manage')
# 成果数据导出
router.register(r'export_data', ExportExcel, basename='export_data')
# 综合启动屏数据统计
router.register(r'count', NumCountView, basename='count')
# 招标信息管理/列表与详情
router.register(r'research', ResearchManageView, basename='research')
# 我的投标信息检索
router.register(r'bid', BidManageView, basename='bid')
# 获得审批的投标信息
router.register(r'get_sp_bid', SPBidHistoryView, basename='get_sp_bid')
# 首页第三屏统计表-机构统计
router.register(r'org_count', ProOrgCountView, basename='org_count')
# 首页第三屏统计表-人员统计
router.register(r'par_count', ProParCountView, basename='par_count')
# 发布招标
router.register(r're_uploads', ResearchUploadView, basename='re_uploads')
# 成果上传
router.register(r'pro_uploads', ProjectsUploadView, basename='pro_uploads')
# 成果详情
# router.register(r'detail', ProDetailView, basename='detail')
# 专家检索
router.register(r'researcher', ParQueryView, basename='researcher')
# 我的专家-增删改
router.register(r'par_manage', ParManageView, basename='par_manage')
# 机构检索
router.register(r'org', OrgQueryView, basename='org')
# 我的机构管理-增删改
router.register(r'org_manage', OrgManageView, basename='org_manage')
# 我的用户
router.register(r'my_user', MyUserView, basename='my_user')
# 注册
router.register(r'register', RegisterView, basename='register')
# 登录
router.register(r'login', LoginView, basename='login')
# 退出登录
router.register(r'login_out', LoginOutView, basename='login_out')
# 热词生成
router.register(r'hot_word', HotWordsView, basename='hot_word')
# 机构或人员详情页-成果定向统计分析
router.register(r'pro_statistics', ProjectsStatisticsView, basename='pro_statistics')
# 投标
router.register(r'bid_uploads', BidderUploadView, basename='bid_uploads')
# 综合统计页面--按年份和类型返回成果对应数量
router.register(r'pro_sts_year', ProjectsStatisticsYearView, basename='pro_sts_year')
# 综合统计页面多线表--按年份和类型返回课题对应数量
router.register(r're_sts_year', ResearchStatisticsYearView, basename='re_sts_year')
# 用户点击数据记录
router.register(r'user_click_sts', UserClickStsView, basename='user_click_sts')
# 用户下载数据记录
router.register(r'user_dwn_sts', UserDownloadStsView, basename='user_dwn_sts')
# 新闻管理
router.register(r'news', NewsManageView, basename='news')
# 课题评审
router.register(r'evaluate', EvaluateBidView, basename='evaluate')

urlpatterns = [
    # 全部注册接口列表
    path(r'', include(router.urls)),
    # 下载次数增加接口
    path(r'download/', projects_download),
    # 查重
    path(r'compare/', compare),
    # 获得成果状态
    path(r'get_compare_status/', get_compare_status),
    # 设置成果状态--包括关系表
    path(r'set_pro_status/', set_pro_status),
    # 设置招标状态
    path(r'set_research_status/', set_research_status),
    # 设置投标状态
    path(r'set_bid_status/', set_bid_status),
    # 设置机构状态
    path(r'set_org_status/', set_org_status),
    # 设置专家状态
    path(r'set_par_status/', set_par_status),
    # 设置用户状态
    path(r'set_user_status/', set_user_status),
    # 查询用户名是否已存在
    path(r'username_search/', user_username_search),
    # 查询同一身份是否被用于同类型账号
    path(r'id_card_search/', user_id_card_search),
    # 验证机构管理员是否存在
    path(r'verify_org_manager/', verify_org_manager_exist),
    # 获得所有机构名称
    path(r'get_org_name/', get_org_name),
    # 测试接口
    path(r'do_something/', do_something),
    # 对内接口-获得所有成果列表
    path(r'get_files/', file_list),
    # 重置密码
    path(r'set_passwd/', set_password),
    # 按照机构属性分别统计有多少所属机构和人员
    path(r'get_ab_org/', get_ab_org),
    # 获取研究人员认证审批状态
    path(r'get_utp_status/', get_user_to_par_status),
    # 获得待审批数量
    path(r'get_pending_approval_count/', get_pending_approval_count),
    # 统计每日操作量
    # path(r'get_daily_logins/', get_daily_logins),
    # 每个机构下挂多少用户
    path(r'get_user_org_groups/', get_user_org_groups),
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
