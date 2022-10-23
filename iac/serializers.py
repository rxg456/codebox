import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, CharField

from . import models


class LoginSerializer(ModelSerializer):
    username = CharField(required=True)
    password = CharField(required=True)

    def is_valid(self, raise_exception=False):
        if super().is_valid(raise_exception):
            username = self.validated_data.pop("username", None)
            password = self.validated_data.pop("password", None)
            user = authenticate(username=username, password=password)
            if user is None:
                if raise_exception:
                    raise ValidationError(code=401)
                return False

            self.validated_data["user"] = user
            self.validated_data["token"] = uuid.uuid4().hex
            self.validated_data["expired_at"] = timezone.now() + timedelta(seconds=settings.TOKEN_ACTIVE_TIME)
            return True

    class Meta:
        model = models.Authorization
        fields = ["username", "password"]


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class AuthorizationSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.Authorization
        fields = ["token", "user", "expired_at"]


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
