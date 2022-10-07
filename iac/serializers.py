from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from . import models


class RepositoryCreationSerializer(ModelSerializer):
    class Meta:
        model = models.Repository
        fields = ["name", "remark", "url"]


class RepositorySerializer(ModelSerializer):
    class Meta:
        model = models.Repository
        fields = "__all__"


class MissionCreationSerializer(ModelSerializer):
    repository = PrimaryKeyRelatedField(queryset=models.Repository.objects.all())

    class Meta:
        model = models.Mission
        fields = ["repository", "playbook"]


class MissionSerializer(ModelSerializer):
    repository = RepositorySerializer(read_only=True)

    class Meta:
        model = models.Mission
        fields = '__all__'
