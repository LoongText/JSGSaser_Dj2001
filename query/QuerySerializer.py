from rest_framework import serializers
from tables.models import Projects


class ProListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ('id', 'name', 'release_date')


class ProCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ('__all__')
