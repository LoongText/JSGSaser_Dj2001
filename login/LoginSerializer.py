from rest_framework import serializers
from tables.models import UserRegister
from jsg import settings


class UserRegisterListSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserRegister
        fields = ['username']


class UserRegisterCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserRegister
        fields = ['roles', 'username', 'id_card_code', 'name', 'cell_phone', 'login_pwd', 'email',
                  'certification_materials']


class UserRegisterRetriveSerializer(serializers.ModelSerializer):

    # roles = serializers.SerializerMethodField()

    class Meta:
        model = UserRegister
        fields = ['roles', 'username', 'id_card_code', 'name', 'cell_phone', 'login_pwd', 'email', 'create_date']

    # @staticmethod
    # def get_roles(obj):
    #     return settings.ROLES_DICT.get(obj.roles)

# class ParRetriveSerializer(serializers.ModelSerializer):
#     unit_name = serializers.ReadOnlyField(source='unit.name')
#
#     class Meta:
#         model = Participant
#         fields = ['name', 'gender', 'unit_name', 'job', 'email', 'brief', 'photo', 'pro_sum']
#
#
# class ParUpdateSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Participant
#         fields = ['name', 'gender', 'job', 'email', 'brief', 'photo']
