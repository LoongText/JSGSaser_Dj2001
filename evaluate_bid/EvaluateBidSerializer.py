from rest_framework import serializers
from tables import models


class EvaluateBidListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BidEvaluation
        fields = ['id']


class EvaluateBidCreateSerializer(serializers.ModelSerializer):

    # operate_user = serializers.SerializerMethodField()

    class Meta:
        model = models.BidEvaluation
        fields = ['relate_bid', 'result', 'stage', 'remarks', 'evaluate_attached']

    # def get_operate_user(self, obj):
    #     operate_user = None
    #     request = self.context.get("request")
    #     if request and hasattr(request, "user"):
    #         operate_user = request.user
    #     print('111', operate_user)
    #     return 1


class EvaluateBidUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BidEvaluation
        fields = ['relate_bid', 'result', 'stage', 'remarks', 'evaluate_attached']


class EvaluateBidRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BidEvaluation
        fields = ['relate_bid', 'designated_experts', 'operate_user', 'result', 'remarks']


class EvaluateBidParSerializer(serializers.ModelSerializer):

    experts_name = serializers.ReadOnlyField(source='designated_experts.name')
    experts_phone = serializers.ReadOnlyField(source='designated_experts.cell_phone')
    experts_job = serializers.ReadOnlyField(source='designated_experts.job')
    experts_unit = serializers.ReadOnlyField(source='designated_experts.unit.name')
    experts_email = serializers.ReadOnlyField(source='designated_experts.email')
    experts_research_direction = serializers.ReadOnlyField(source='designated_experts.research_direction')

    class Meta:
        model = models.BidEvaluation
        fields = ['designated_experts', 'experts_name', 'experts_phone', 'experts_job', 'experts_unit', 'experts_email',
                  'experts_research_direction']


class EvaluateBidParReviewSerializer(serializers.ModelSerializer):

    experts_name = serializers.ReadOnlyField(source='designated_experts.name')
    experts_phone = serializers.ReadOnlyField(source='designated_experts.cell_phone')
    experts_unit = serializers.ReadOnlyField(source='designated_experts.unit.name')

    class Meta:
        model = models.BidEvaluation
        fields = ['designated_experts', 'experts_name', 'experts_phone', 'experts_unit', 'remarks',
                  'evaluate_attached', 'result']