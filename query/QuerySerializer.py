from rest_framework import serializers
from tables.models import Projects, UserRegister, User
from django.contrib.auth .models import Group, AnonymousUser


class ProListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ('id', 'name', 'release_date')


class ProCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ['__all__']


class UserRetrieveSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    # org_name = serializers.SerializerMethodField()
    # par_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'org', 'par', 'date_joined', 'last_login', 'is_active', 'roles',
                  'id_card', 'cell_phone', 'email']

    @staticmethod
    def get_roles(obj):
        """获取用户角色-所属组"""
        roles_obj = obj.groups.all().first()
        return roles_obj.id if roles_obj else None

    @staticmethod
    def get_is_active(obj):
        """将is_active传过来的true和false改为1和0"""
        return 1 if obj.is_active is True else 0

    # @staticmethod
    # def get_org_name(obj):
    #     """获取认证机构"""
    #     org_obj = obj.org
    #     return org_obj.name if org_obj else None
    #
    # @staticmethod
    # def get_par_name(obj):
    #     """获取认证专家"""
    #     par_obj = obj.par
    #     return par_obj.name if par_obj else None


class UserRegisterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegister
        fields = ['__all__']


class GoodProListSerializer(serializers.ModelSerializer):
    good_mark__remarks = serializers.SerializerMethodField()
    classify__cls_name = serializers.SerializerMethodField()
    user__first_name = serializers.SerializerMethodField()
    research = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        fields = ['uuid', 'name', 'classify__cls_name', 'key_word', 'good_mark__remarks',
                  'release_date', 'user__first_name', 'views', 'downloads', 'research']

    @staticmethod
    def get_good_mark__remarks(obj):
        """获取优秀成果标签名称"""
        good_mark_obj = obj.good_mark
        return good_mark_obj.remarks if good_mark_obj else None

    @staticmethod
    def get_classify__cls_name(obj):
        """获取分类名称"""
        cls_name_obj = obj.classify
        return cls_name_obj.cls_name if cls_name_obj else None

    @staticmethod
    def get_user__first_name(obj):
        """获取用户名称"""
        user_obj = obj.user
        return user_obj.first_name if user_obj else None

    @staticmethod
    def get_research(obj):
        """获取研究机构名称"""
        research_obj = obj.research.all()
        return [i.name for i in research_obj]
