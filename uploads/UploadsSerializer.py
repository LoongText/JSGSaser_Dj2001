from rest_framework import serializers
from tables.models import Research, Projects, Bid, Organization, Participant, User


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


class OrgListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['name']


class OrgCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['name', 'nature', 'is_a', 'is_b', 'brief', 'is_show', 'photo']


class OrgRetriveSerializer(serializers.ModelSerializer):
    nature_remarks = serializers.ReadOnlyField(source='nature.remarks')

    class Meta:
        model = Organization
        fields = ['name', 'is_a', 'is_b', 'brief', 'pro_sum', 'par_sum', 'nature_remarks', 'photo']


class OrgUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['nature', 'is_a', 'is_b', 'brief', 'photo']


class ParListSerializer(serializers.ModelSerializer):

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
