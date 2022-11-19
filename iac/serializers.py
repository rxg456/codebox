import json
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
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
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

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
        fields = ["repository", "playbook", "inventories"]


class MissionEventSerializer(ModelSerializer):
    class Meta:
        model = models.MissionEvent
        fields = '__all__'


class MissionSerializer(ModelSerializer):
    repository = RepositorySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = models.Mission
        fields = '__all__'


class MissionWithEventsSerializer(ModelSerializer):
    repository = RepositorySerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    events = MissionEventSerializer(read_only=True, many=True)

    class Meta:
        model = models.Mission
        fields = '__all__'


class IntervalSerializer(ModelSerializer):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'


class CrontabSerializer(ModelSerializer):
    class Meta:
        model = CrontabSchedule
        exclude = ['timezone']


class SchedulerSerializer(ModelSerializer):
    interval = IntervalSerializer(required=False)
    crontab = CrontabSerializer(required=False)

    class Meta:
        model = PeriodicTask
        fields = ["interval", "crontab", "enabled"]

    def is_valid(self, raise_exception=False):
        if not super(SchedulerSerializer, self).is_valid(raise_exception):
            return False
        interval_data = self.validated_data.pop("interval", None)
        crontab_data = self.validated_data.pop("crontab", None)
        # interval和crontab必须有一个
        if len([x for x in (interval_data, crontab_data) if x is not None]) != 1:
            if raise_exception:
                raise ValidationError("interval and crontab required 1")
            return False

        if interval_data is not None:
            interval_serializer = IntervalSerializer(data=interval_data)
            if interval_serializer.is_valid(raise_exception):
                interval_serializer.save()
                self.validated_data["interval"] = interval_serializer.instance
            else:
                return False
        if crontab_data is not None:
            crontab_serializer = CrontabSerializer(data=crontab_data)
            if crontab_serializer.is_valid(raise_exception):
                crontab_serializer.save()
                self.validated_data["crontab"] = crontab_serializer.instance
            else:
                return False
        return True


class PeriodicMissionCreationSerializer(ModelSerializer):
    repository = PrimaryKeyRelatedField(queryset=models.Repository.objects.all())
    scheduler = SchedulerSerializer(required=True)

    class Meta:
        model = models.PeriodicMission
        fields = ["repository", "playbook", "inventories", "scheduler"]

    def is_valid(self, raise_exception=False):
        if not super(PeriodicMissionCreationSerializer, self).is_valid(raise_exception):
            return False
        uid = uuid.uuid4()
        self.validated_data["uuid"] = uid

        scheduler_data = self.validated_data.pop("scheduler", None)
        if scheduler_data is None:
            if raise_exception:
                raise ValidationError("scheduler is required")
            return False
        ser = SchedulerSerializer(data=scheduler_data)
        if ser.is_valid(raise_exception):
            ser.save(name=uid.hex, args=json.dumps([uid.hex]), task="iac.tasks.submit")
        else:
            return False
        self.validated_data["scheduler"] = ser.instance
        return True


class PeriodicMissionSerializer(ModelSerializer):
    repository = RepositorySerializer(read_only=True)
    scheduler = SchedulerSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = models.PeriodicMission
        fields = "__all__"


class PeriodicMissionMutationSerializer(MutationSerializerMixin, PeriodicMissionCreationSerializer):
    class Meta:
        model = models.PeriodicMission
        fields = ["repository", "playbook", "inventories", "scheduler"]
