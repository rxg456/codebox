from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from . import models


class MutationSerializerMixin:
    def get_fields(self):
        fields = {}
        for name, field in super().get_fields().items():
            field.required = False
            fields[name] = field
        return fields


class RepositoryCreationSerializer(ModelSerializer):
    class Meta:
        model = models.Repository
        fields = ["name", "remark", "url"]


class RepositorySerializer(ModelSerializer):
    class Meta:
        model = models.Repository
        fields = "__all__"


class RepositoryMutationSerializer(MutationSerializerMixin, ModelSerializer):
    class Meta:
        model = models.Repository
        fields = ["name", "remark"]


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
