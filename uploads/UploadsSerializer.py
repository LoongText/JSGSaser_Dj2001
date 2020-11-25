from rest_framework import serializers
from jsg import settings
from django.contrib.auth .models import AnonymousUser
from tables import models


class BaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Research
        fields = ('name',)


class BaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Research
        fields = ['name', 'classify', 'start_date', 'end_date', 'status', 'guidelines',
                  'funds', 'brief', 'contacts', 'phone', 'user']


class BaseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Research
        fields = ['classify', 'start_date', 'end_date', 'status', 'guidelines',
                  'funds', 'brief', 'contacts', 'phone']


class ProListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Projects
        fields = ['id', 'name']


class ProRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Projects
        fields = ['id', 'name']


class ProCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Projects
        fields = ['name', 'attached', 'status', 'user']


class ProUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Projects
        fields = ['lead_org', 'research', 'classify', 'key_word', 'bid']


class BidderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bid
        fields = ['id', 're_title']


class BidderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bid
        fields = ['bidder', 'bidding', 'funds', 'contacts', 'con_phone', 'bidder_date',
                  'brief', 'submitter', 'leader', 'lea_phone', 're_title', 'bidder_status']


class BidderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Bid
        fields = ['funds', 'contacts', 'con_phone', 'bidder_date',
                  'brief', 'leader', 'lea_phone', 're_title', 'bidder_status']


class BidderRetirveSerializer(serializers.ModelSerializer):
    bidding_name = serializers.ReadOnlyField(source='bidding.name')
    submitter_name = serializers.ReadOnlyField(source='submitter.username')

    class Meta:
        model = models.Bid
        fields = "__all__"


class OrgPersonalListSerializer(serializers.ModelSerializer):

    superior_unit = serializers.SerializerMethodField()
    nature__remarks = serializers.SerializerMethodField()

    class Meta:
        model = models.Organization
        fields = ['id', 'uuid', 'name', 'superior_unit', 'nature__remarks']

    @staticmethod
    def get_nature__remarks(obj):
        """
        机构性质
        :param obj:
        :return:
        """
        return obj.nature.remarks if obj.nature else None

    @staticmethod
    def get_superior_unit(obj):
        """
        上级单位--不与主管部门同时显示
        :param obj:
        :return:
        """
        org_id = obj.superior_unit
        superior_unit_obj = models.Organization.objects.values('name').filter(pk=org_id)
        if superior_unit_obj:
            superior_unit_org = superior_unit_obj[0]['name']
        else:
            superior_unit_org = ''
        return superior_unit_org


class OrgCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Organization
        fields = ['name', 'nature', 'superior_unit', 'brief', 'is_show', 'photo']


class OrgRetriveSerializer(serializers.ModelSerializer):
    nature_remarks = serializers.ReadOnlyField(source='nature.remarks')
    subordinate_unit = serializers.SerializerMethodField()
    superior_unit = serializers.SerializerMethodField()

    class Meta:
        model = models.Organization
        fields = ['name', 'superior_unit', 'brief', 'pro_sum', 'par_sum', 'nature_remarks', 'photo',
                  'subordinate_unit', 'id_card_code','register_type', 'register_capital', 'register_date', 'address',
                  'postcode', 'unit_tel', 'unit_fax', 'certification_materials', 'business_license']

    @staticmethod
    def get_subordinate_unit(obj):
        """
        下级单位
        :param obj:
        :return:
        """
        org_id_list = [obj.id]
        subordinate_unit = []
        for org_id in org_id_list:
            subordinate_unit_obj = models.Organization.objects.values('id', 'name').filter(superior_unit=org_id)
            subordinate_unit_name = [i['name'] for i in subordinate_unit_obj]
            subordinate_unit_id = [i['id'] for i in subordinate_unit_obj]
            org_id_list.extend(subordinate_unit_id)
            subordinate_unit.extend(subordinate_unit_name)
        return subordinate_unit

    @staticmethod
    def get_superior_unit(obj):
        """
        上级单位-不与主管部门同时显示
        :param obj:
        :return:
        """
        return obj.superior_unit


class OrgUpdateSerializer(serializers.ModelSerializer):
    # id_card_code = serializers.SerializerMethodField()

    class Meta:
        model = models.Organization
        fields = ['id_card_code', 'name', 'nature', 'superior_unit', 'brief', 'photo', 'par_sum', 'pro_sum', 'is_show',
                  'register_type', 'register_capital', 'register_date', 'address', 'postcode', 'unit_tel', 'unit_fax',
                  'business_license']

    def validate_id_card_code(self, attrs):

        """
        验证身信用代码--只能由超管修改，其他用户该是原来的值
        :param attrs: 接收的参数
        :return:
        """
        request = self.context["request"]
        user = request.user
        compare_list = [user.is_superuser, settings.SUPER_USER_GROUP]
        return self._general_validate_method(user, self.instance.id_card_code, attrs, compare_list)

    def validate_name(self, attrs):

        """
        验证名称--只能由超管修改，其他用户该是原来的值
        :param attrs: 接收的参数
        :return:
        """
        request = self.context["request"]
        user = request.user
        compare_list = [user.is_superuser, settings.SUPER_USER_GROUP]
        return self._general_validate_method(user, self.instance.name, attrs, compare_list)

    def validate_business_license(self, attrs):

        """
        验证营业执照--只能由超管修改，其他用户该是原来的值
        :param attrs: 接收的参数
        :return:
        """
        request = self.context["request"]
        user = request.user
        compare_list = [user.is_superuser, settings.SUPER_USER_GROUP]
        return self._general_validate_method(user, self.instance.business_license, attrs, compare_list)

    def validate_par_sum(self, attrs):

        """
        验证研究人员数量--只能由超管修改，其他用户该是原来的值
        :param attrs: 接收的参数
        :return:
        """
        request = self.context["request"]
        user = request.user
        compare_list = [user.is_superuser, settings.SUPER_USER_GROUP]
        return self._general_validate_method(user, self.instance.par_sum, attrs, compare_list)

    def validate_pro_sum(self, attrs):

        """
        验证研究成果数量--只能由超管修改，其他用户该是原来的值
        :param attrs: 接收的参数
        :return:
        """
        request = self.context["request"]
        user = request.user
        compare_list = [user.is_superuser, settings.SUPER_USER_GROUP]
        return self._general_validate_method(user, self.instance.pro_sum, attrs, compare_list)

    def validate_is_show(self, attrs):

        """
        验证是否可用--只能由超管修改，其他用户该是原来的值
        :param attrs: 接收的参数
        :return:
        """
        request = self.context["request"]
        user = request.user
        compare_list = [user.is_superuser, settings.SUPER_USER_GROUP, settings.PLANT_MANAGER_GROUP]
        return self._general_validate_method(user, self.instance.is_show, attrs, compare_list)

    @staticmethod
    def _general_validate_method(user, ori_attrs, new_attrs, compare_list):
        """
        验证通用方法--简化步骤
        :param user: 用户对象
        :param ori_attrs: 原值
        :param new_attrs: 接收值
        :param compare_list: 允许修改角色id列表
        :return: 最终修改值
        """
        if type(user) == AnonymousUser:
            raise serializers.ValidationError('未获取到用户')
        group_id_obj = user.groups.all().first()
        group_id = group_id_obj.id if group_id_obj else 0
        if group_id in compare_list:
            return new_attrs
        else:
            return ori_attrs


class ParListPersonalSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Participant
        fields = ['name']


class ParCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Participant
        fields = ['name', 'id_card', 'cell_phone', 'gender', 'unit', 'job', 'email', 'brief', 'photo', 'birth',
                  'education', 'academic_degree', 'address', 'postcode', 'research_direction',
                  'id_card_photo_positive', 'id_card_photo_reverse']


class ParRetriveSerializer(serializers.ModelSerializer):
    unit_name = serializers.ReadOnlyField(source='unit.name')

    class Meta:
        model = models.Participant
        fields = ['name', 'gender', 'unit_name', 'job', 'email', 'brief', 'photo', 'pro_sum', 'id_card', 'cell_phone',
                  'birth', 'education', 'academic_degree', 'address', 'postcode', 'research_direction',
                  'id_card_photo_positive', 'id_card_photo_reverse']


class ParUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Participant
        fields = ['gender', 'unit', 'job', 'email', 'brief', 'photo', 'cell_phone',
                  'birth', 'education', 'academic_degree', 'address', 'postcode', 'research_direction']


class NewsTextList2Serializer(serializers.ModelSerializer):

    class Meta:
        model = models.News
        fields = ['id', 'title']


class NewsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.News
        fields = ['title', 'text_attached', 'text_create_time']


class NewsUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.News
        fields = ['image_attached']


class NewsRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.News
        fields = ['title']