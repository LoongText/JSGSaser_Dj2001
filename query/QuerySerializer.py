from rest_framework import serializers
from tables.models import Projects, UserRegister, User, UserToParticipant
from django.contrib.auth .models import Group, AnonymousUser
from jsg import settings

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
    is_par_ing = serializers.SerializerMethodField()
    # par_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'org', 'par', 'date_joined', 'last_login', 'is_active', 'roles',
                  'id_card', 'cell_phone', 'email', 'photo', 'is_par_ing']

    @staticmethod
    def get_roles(obj):
        """获取用户角色-所属组"""
        roles_obj = obj.groups.all().first()
        return {"role_id": roles_obj.id,"role_name": roles_obj.name} if roles_obj else None

    @staticmethod
    def get_is_active(obj):
        """将is_active传过来的true和false改为1和0"""
        return 1 if obj.is_active is True else 0

    @staticmethod
    def get_is_par_ing(obj):
        """针对普通个人用户-是否正在进行研究人员认证审批"""
        obj_tmp = UserToParticipant.objects.filter(user=obj.id, up_status=0)
        return 1 if obj_tmp else 0

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


class UserToParCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToParticipant
        fields = ['gender', 'birth', 'education', 'academic_degree', 'address', 'postcode', 'brief', 'user',
                  'research_direction', 'photo', 'id_card_photo_positive', 'id_card_photo_reverse', 'job_certi']


class UserToParListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    cell_phone = serializers.SerializerMethodField()
    up_status = serializers.SerializerMethodField()

    class Meta:
        model = UserToParticipant
        fields = ['id', 'name', 'cell_phone', 'created_date', 'up_status']

    @staticmethod
    def get_up_status(obj):
        # 此处状态码和注册用一样的
        return settings.REGISTER_APPROVAL_RESULT.get(obj.up_status)

    @staticmethod
    def get_name(obj):
        return obj.user.first_name

    @staticmethod
    def get_cell_phone(obj):
        return obj.user.cell_phone
