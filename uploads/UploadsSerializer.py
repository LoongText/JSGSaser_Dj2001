from rest_framework import serializers
from tables.models import Research, Projects, Bid, Organization, Participant, News
from jsg import settings
from django.contrib.auth .models import Group


class BaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ('name',)


class BaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ['name', 'classify', 'start_date', 'end_date', 'status', 'guidelines',
                  'funds', 'brief', 'contacts', 'phone', 'user']


class BaseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ['classify', 'start_date', 'end_date', 'status', 'guidelines',
                  'funds', 'brief', 'contacts', 'phone']


class ProListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id', 'name']


class ProRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id', 'name']


class ProCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ['name', 'attached', 'status', 'user']


class ProUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ['lead_org', 'research', 'classify', 'key_word', 'bid']


class BidderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['id', 're_title']


class BidderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['bidder', 'bidding', 'funds', 'contacts', 'con_phone', 'bidder_date',
                  'brief', 'submitter', 'leader', 'lea_phone', 're_title', 'bidder_status']


class BidderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['funds', 'contacts', 'con_phone', 'bidder_date',
                  'brief', 'leader', 'lea_phone', 're_title', 'bidder_status']


class BidderRetirveSerializer(serializers.ModelSerializer):
    bidding_name = serializers.ReadOnlyField(source='bidding.name')
    submitter_name = serializers.ReadOnlyField(source='submitter.username')

    class Meta:
        model = Bid
        fields = "__all__"


class OrgPersonalListSerializer(serializers.ModelSerializer):

    competent_dpt = serializers.SerializerMethodField()
    superior_unit = serializers.SerializerMethodField()
    nature__remarks = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ['id', 'uuid', 'name', 'competent_dpt', 'superior_unit', 'nature__remarks']

    @staticmethod
    def get_nature__remarks(obj):
        """
        机构性质
        :param obj:
        :return:
        """
        return obj.nature.remarks if obj.nature else None

    @staticmethod
    def get_competent_dpt(obj):
        """
        主管部门
        :param obj:
        :return:
        """
        org_id = obj.competent_dpt
        competent_dpt_obj = Organization.objects.values('name').filter(pk=org_id)
        if competent_dpt_obj:
            competent_dpt_org = competent_dpt_obj[0]['name']
        else:
            competent_dpt_org = ''
        return competent_dpt_org

    @staticmethod
    def get_superior_unit(obj):
        """
        上级单位--不与主管部门同时显示
        :param obj:
        :return:
        """
        if obj.competent_dpt:
            return None
        org_id = obj.superior_unit
        superior_unit_obj = Organization.objects.values('name').filter(pk=org_id)
        if superior_unit_obj:
            superior_unit_org = superior_unit_obj[0]['name']
        else:
            superior_unit_org = ''
        return superior_unit_org


class OrgCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['name', 'nature', 'competent_dpt', 'superior_unit', 'brief', 'is_show', 'photo']


class OrgRetriveSerializer(serializers.ModelSerializer):
    nature_remarks = serializers.ReadOnlyField(source='nature.remarks')
    subordinate_unit = serializers.SerializerMethodField()
    superior_unit = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ['name', 'competent_dpt', 'superior_unit', 'brief', 'pro_sum', 'par_sum', 'nature_remarks', 'photo',
                  'subordinate_unit']

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
            subordinate_unit_obj = Organization.objects.values('id', 'name').filter(superior_unit=org_id)
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
        if obj.competent_dpt:
            return 0
        else:
            return obj.superior_unit


class OrgUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['nature', 'competent_dpt', 'superior_unit', 'brief', 'photo']


class ParListPersonalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participant
        fields = ['name']


class ParCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participant
        fields = ['name', 'gender', 'unit', 'job', 'email', 'brief', 'photo']


class ParRetriveSerializer(serializers.ModelSerializer):
    unit_name = serializers.ReadOnlyField(source='unit.name')

    class Meta:
        model = Participant
        fields = ['name', 'gender', 'unit_name', 'job', 'email', 'brief', 'photo', 'pro_sum']


class ParUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Participant
        fields = ['name', 'gender', 'job', 'email', 'brief', 'photo']


# class NewsTextListSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = News
#         fields = ['id', 'title', 'text_create_time']


class NewsTextList2Serializer(serializers.ModelSerializer):

    class Meta:
        model = News
        fields = ['id', 'title']


# class NewsImageListSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = News
#         fields = ['id', 'title', 'image_attached', 'text_create_time']


class NewsCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = News
        fields = ['title', 'text_attached', 'text_create_time']


class NewsUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = News
        fields = ['image_attached']


class NewsRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = News
        fields = ['title']