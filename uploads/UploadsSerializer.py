from rest_framework import serializers
from tables.models import Research, Projects, Bid


class BaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ('name',)


class BaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ['name', 'classify', 'start_date', 'end_date', 'status', 'guidelines', 'funds', 'brief', 'contacts', 'phone', 'user']


class BaseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Research
        fields = ['name', 'classify', 'start_date', 'end_date', 'status', 'guidelines', 'funds', 'brief', 'contacts', 'phone', 'user']


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


# class lead_orgSer(ser)
#     class Meta:
#         model = Projects
#         fie

class ProUpdateSerializer(serializers.ModelSerializer):
    # lead_org = lead_orgSer
    class Meta:
        model = Projects
        fields = ['lead_org', 'research', 'classify', 'key_word', 'bid']


class BidderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['id', 'bidder']


class BidderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['bidder', 'bidding', 'funds', 'contacts', 'con_phone', 'bidder_date',
                  'brief', 'submitter', 'leader', 'lea_phone', 're_title', 'bidder_status']
