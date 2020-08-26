from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from query.views import *
from uploads.views import *
from login.views import *
from gather_statistics.views import *
from check.views import *
from status_operation.views import *
from django.urls import re_path
from django.views.static import serve

router = routers.DefaultRouter()
# 成果检索
router.register(r'query', ProjectsQueryView, basename='query')
# 我的成果检索
router.register(r'my_query', MyProjectsQueryView, basename='my_query')
# 综合启动屏数据统计
router.register(r'count', NumCountView, basename='count')
# 招标信息检索
router.register(r'search', ResearchQueryView, basename='search')
# 我的投标信息
router.register(r'my_bid', MyBidQueryView, basename='my_bid')
# 获得审批的投标信息
router.register(r'get_sp_bid', SPBidHistoryView, basename='get_sp_bid')
# 招标检索
router.register(r'bid', BidQueryView, basename='bid')
# 首页第三屏统计表-机构统计
router.register(r'org_count', ProOrgCountView, basename='org_count')
# 首页第三屏统计表-人员统计
router.register(r'par_count', ProParCountView, basename='par_count')
# 发布招标
router.register(r're_uploads', ResearchUploadView, basename='re_uploads')
# 成果上传
router.register(r'pro_uploads', ProjectsUploadView, basename='pro_uploads')
# 成果详情
router.register(r'detail', ProDetailView, basename='detail')
# 专家检索
router.register(r'researcher', PaticipantsQueryView, basename='researcher')
# 推荐专家
router.register(r'rcd_researcher', ParticipantsRcdView, basename='rcd_researcher')
# 机构检索
router.register(r'org', OrgQueryView, basename='org')
# 推荐机构
router.register(r'rcd_org', OrgRcdView, basename='rcd_org')
# 登录
router.register(r'login', LoginView, basename='login')
# 退出登录
router.register(r'login_out', LoginOutView, basename='login_out')
# 热词生成
router.register(r'hot_word', HotWordsView, basename='hot_word')
# 成果修改
# router.register(r'pro_update', ProjectsUpdateView, basename='pro_update')
# 招标详情页
router.register(r're_detail', ResearchDetailView, basename='re_detail')
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
    # 设置成果状态恢复--包括关系表
    # path(r'set_recovery_status/', set_recovery_status),
    # 成果上传2-添加基本信息--修改
    path(r'pro_update_base_info/', pro_update_base_info),
    # 成果上传3-添加课题小组--修改
    path(r'pro_update_pars/', pro_update_pars),
    # 测试接口
    path(r'do_something/', do_something),
    # 对内接口-获得所有成果列表
    path(r'get_files/', file_list),
    # 重置密码
    path(r'set_passwd/', set_passwd),
    # 按照机构属性分别统计有多少所属机构和人员
    path(r'get_ab_org/', get_ab_org),
    # 后台；
    # path('admin/', admin.site.urls),
    # 自定义后台
    path('back/', include('backstage.urls')),
    # path('admin/', xadmin.site.urls),
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
