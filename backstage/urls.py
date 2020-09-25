from django.urls import path
from . import views
from django.views.generic.base import RedirectView

app_name = 'back'
urlpatterns = [
    # 登录
    path(r'login/', views.user_login, name='login'),
    path(r'login_out/', views.login_out, name='login_out'),
    path(r'get_login_status/', views.get_login_status, name='get_login_status'),
    # 首页
    path(r'', views.main, name='main'),
    # 成果管理
    path(r'pm', views.projects_manage, name='pm'),
    path(r'pd', views.project_detail, name='pd'),
    path(r'pdel', views.project_del, name='pdel'),
    path(r'pwd', views.project_withdraw, name='pwd'),  # 管理员撤回成--将合格状态的成果转化为未完善状态
    path(r'pm_e/<str:uuid>', views.project_edit, name='pm_e'),
    path(r'pm_ed', views.project_edit_do, name='pm_ed'),
    path(r'psp', views.project_sp, name='psp'),
    path(r'pro_rel_del', views.pro_relations_del, name='pro_rel_del'),
    path(r'pro_add', views.pro_add, name='pro_add'),
    path(r'good_pro_mng', views.good_project_manage, name='good_pro_mng'),
    path(r'choose_good_project', views.choose_good_project_manage, name='choose_good_project'),
    # 招标管理
    path(r'rm', views.research_manage, name='rm'),
    path(r'rd', views.research_detail, name='rd'),
    path(r'rdel', views.research_del, name='rdel'),
    path(r'rm_e/<str:uuid>', views.research_edit, name='rm_e'),
    path(r'rm_ed', views.research_edit_do, name='rm_ed'),
    path(r'rm_bid', views.research_bid_manage, name='rm_bid'),
    path(r'rm_bid_jt', views.research_bid_jt_manage, name='rm_bid_jt'),
    path(r'rm_sp_his/<str:param>', views.research_sp_history, name='rm_sp_his'),  # 申请审批记录
    path(r'rm_add', views.research_add, name='rm_add'),
    # 投标管理
    path(r'bm', views.bid_manage, name='bm'),
    path(r'bd', views.bid_detail, name='bd'),
    path(r'bdel', views.bid_del, name='bdel'),
    path(r'bm_e/<int:edit_id>', views.bid_edit, name='bm_e'),
    path(r'bm_ed', views.bid_edit_do, name='bm_ed'),
    path(r'bm_ac', views.bid_apply_conclusion, name='bm_ac'),
    path(r'bid_search', views.bid_search, name='bid_search'),
    # 研究人员管理
    path(r'parm', views.participant_manage, name='parm'),
    path(r'parmd', views.participant_detail, name='parmd'),
    path(r'parmdel', views.participant_del, name='parmdel'),
    path(r'parm_e/<str:uuid>', views.participant_edit, name='parm_e'),
    path(r'parm_ed', views.participant_edit_do, name='parm_ed'),
    path(r'par_add', views.participant_add, name='par_add'),
    path(r'par_search', views.participant_search, name='par_search'),
    # 用户管理
    path(r'user', views.user_manage, name='user'),
    path(r'user_add', views.user_add, name='user_add'),
    path(r'userd', views.user_detail, name='userd'),
    path(r'userdel', views.user_del, name='userdel'),
    path(r'user_e/<str:uuid>', views.user_edit, name='user_e'),
    path(r'user_ed', views.user_edit_do, name='user_ed'),
    path(r'user_org', views.user_org_search, name='user_org'),
    path(r'user_uname', views.user_username_search, name='user_uname'),
    path(r'user_mp/<str:uuid>', views.user_modify_password, name='user_mp'),
    path(r'get_daily_user', views.get_daily_login_user, name='get_daily_user'),
    # 机构管理
    path(r'org', views.org_manage, name='org'),
    path(r'orgd', views.org_detail, name='orgd'),
    path(r'org_add', views.org_add, name='org_add'),
    path(r'orgdel', views.org_del, name='orgdel'),
    path(r'org_e/<str:uuid>', views.org_edit, name='org_e'),
    path(r'org_search', views.org_search, name='org_search'),
    # path('to_start_screen/', RedirectView.as_view(url='http://10.170.128.150/static/jsg-dist/index.html#/'), name='login_out_re'),
    # login.js也要修改
    # path('to_start_screen/', RedirectView.as_view(url='http://wlaq.cnki.net/vue-jsg/#/'), name='to_start_screen'),
    path('to_start_screen/', RedirectView.as_view(url='https://iser.cnki.net/'), name='to_start_screen'),
    # path('to_start_screen/', RedirectView.as_view(url='http://10.170.128.108:8088/static/dist/index.html#/'), name='to_start_screen'),
]
