"""
Django settings for jsg project.

Generated by 'django-admin startproject' using Django 2.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7vq=89q*a_keq3h=*7&$s*t_q6f6$bm5+zqt22^g2+k+wcl_4*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    # 'simplepro',
    # 'simpleui',
    # 'import_export',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'tables',
    'query',
    'uploads',
    'corsheaders',
    # 'guardian',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'simplepro.middlewares.SimpleMiddleware'
]

# AUTHENTICATION_BACKENDS = (
#     'django.contrib.auth.backends.ModelBackend', # default
#     # 'guardian.backends.ObjectPermissionBackend',
# )

ROOT_URLCONF = 'jsg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'jsg.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': 'cnki_2001_jsg_dev',
        # 'USER': 'postgres',
        # 'PASSWORD': 'postgres',
        # 'HOST': '101.200.126.33',
        'NAME': 'cnki_2001_jsg_pro',
        'USER': 'postgres',
        'PASSWORD': 'cnki5722902',
        'HOST': '192.168.105.28',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #      # 验证密码和用户名相似度
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        # 验证密码最少长度
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        # 'OPTIONS': {
        #     'min_length': 9,
        # }
    },
    # {
    #     # 密码是否出现在常用密码中
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    {
        # 密码不能全是数字
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'media')
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # 即项目路径下的media文件夹，没有则自动创建
MEDIA_URL = '/media/'  # 这个是在浏览器上访问该上传文件的url的前缀

APPEND_SLASH = False

# 跨域问题
CORS_ORIGIN_ALLOW_ALL = True

REST_FRAMEWORK = {
    # 新增的
    # 'DEFAULT_AUTHENTICATION_CLASSES': (
    #     'login.auth.ExpiringTokenAuthentication',   # 根据自己的实际情况填写路径
    # ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}

# 停用词路径
STOP_WORD_PATHS = os.path.join(BASE_DIR, 'login')

# 定时任务
# '*/1 * * * *'每一分钟执行一次
# '10 12 * * *'12点10分执行
CRONJOBS = [
    ('0 4 * * *', 'login.cron.cron.create_hotword', '>> /www/govin/logs/crontab.log'),
]

PUN_LIST = [
    '。', '，', '、', '？', '！', '；', '：', '“', '”', '‘', '’', '「', '」', '『', '』', '（', '）', '[', ']',

    '〔', '〕', '【', '】', '——', '—', '……', '…', '—', '-', '～', '·', '《', '》', '〈', '〉', '﹏﹏', '___',

    '.',
]

CLUE_KEYWORDS_LIST = [
    "总之", "总而言之", "报导", "新华社", "报道", "定金",
]

HOPE_KEYWORDS_LIST = [
    "恭请", "请求领导", "紧急求助", "要严查", "公正的答复", "协助我们", "希望政府", "保证我们", "我们希望", "我们恳求", "诚心恳请",
    "希望", "我期待", "请省长", "请市长", "还希望", "能不能", "是否可以", "恳请领导", "希望领导", "希望",
]

# 日志文件设置
# BASE_LOG_DIR = os.path.join(BASE_DIR, "logs")
# LOGGING = {
#     # 保留字
#     'version': 1,
#     # 禁用已经存在的logger实例
#     'disable_existing_loggers': False,
#     # 日志文件的格式
#     'formatters': {
#         # 详细的日志格式
#         'standard': {
#             'format': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]'
#                       '[%(levelname)s][%(message)s]'
#         },
#         # 简单的日志格式
#         'simple': {
#             'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
#         },
#         # 定义一个特殊的日志格式
#         'collect': {
#             'format': '%(message)s'
#         }
#     },
#     # 过滤器
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#     },
#     # 处理器
#     'handlers': {
#         # 在终端打印
#         'console': {
#             'level': 'DEBUG',
#             # 只有在Django debug为True时才在屏幕打印日志
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple'
#         },
#         # 默认的
#         'default': {
#             'level': 'INFO',
#             # 保存到文件，自动切
#             'class': 'logging.handlers.RotatingFileHandler',
#             # 日志文件
#             'filename': os.path.join(BASE_LOG_DIR, "info.log"),
#             # 日志大小50M
#             'maxBytes': 1024 * 1024 * 50,
#             # 最多备份几个
#             'backupCount': 3,
#             'formatter': 'standard',
#             'encoding': 'utf-8',
#         },
#         # 专门用来记错误日志
#         'error': {
#             'level': 'ERROR',
#             # 保存到文件，自动切
#             'class': 'logging.handlers.RotatingFileHandler',
#             # 日志文件
#             'filename': os.path.join(BASE_LOG_DIR, "errors.log"),
#             # 日志大小50m
#             'maxBytes': 1024 * 1024 * 50,
#             'backupCount': 5,
#             'formatter': 'standard',
#             'encoding': 'utf-8',
#         },
#     },
#     'loggers': {
#         # 默认的logger应用如下配置
#         '': {
#             # 上线之后可以把'console'移除
#             'handlers': ['default', 'console', 'error'],
#             'level': 'INFO',
#             # 向不向更高级别的logger传递
#             'propagate': True,
#         },
#     },
# }

SIMPLEPRO_INFO = False
# SIMPLEUI_HOME_PAGE = 'https://www.sunwu.zone'
SIMPLEUI_ICON = {
    '成果信息表': 'fas fa-user-tie',
    '表': 'fab fa-docker',
    '日志记录': 'fas fa-flask',
    '认证令牌': 'fas fa-fingerprint',
    '令牌': 'fas fa-fingerprint',

    '课题信息表': 'fas fa-book-open',

    '研究人员信息表': 'fas fa-graduation-cap',

    '热词表': 'fas fa-fire-alt',

    '敏感词表': 'fas fa-skull-crossbones',

}

# 让 Django 用户认证系统使用自定义的用户模型
AUTH_USER_MODEL = 'tables.User'

PROJECTS_STATUS_CHOICE = {0: '不显示', 1: '合格', 2: '待完善', 3: '检测中', 4: '不合格', 5: '删除'}
RESEARCH_STATUS_CHOICE = {0: '未开启', 1: '招标中', 2: '推进中', 3: '已结题', 4: '删除'}
BIDDER_STATUS_CHOICE = {0: '暂存', 1: '投标中', 2: '中标', 3: '未中标', 4: '删除'}
BIDDER_CONCLUSION_STATUS = {0: '未开始', 1: '审批中', 2: '已通过', 3: '未通过'}
PRO_RELATIONS_ROLES = {1: '组长', 2: '副组长', 3: '组员'}

ORG_NATURE_LOWER_LEVEL = 4
ORG_NATURE_HIGHER_LEVEL = 1
ORG_GROUP_LOWER_LEVEL = 4
ORG_GROUP_SUPERUSER_LEVEL = 1
ORG_GROUP_MANAGER_LEVEL = 2