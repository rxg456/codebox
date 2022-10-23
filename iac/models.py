from django.contrib.auth.models import User
from django.db import models


class TimestampMinIn(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Repository(models.Model):
    name = models.CharField(max_length=32, unique=True)
    remark = models.CharField(max_length=512, null=True)
    url = models.CharField(max_length=512, null=True)


class MissionState(models.IntegerChoices):
    PENDING = 0, 'PENDING'
    RUNNING = 1, 'RUNNING'
    COMPLETED = 2, 'COMPLETED'
    FAILED = 3, 'FAILED'
    CANCELED = 4, 'CANCELED'
    TIMEOUT = 5, 'TIMEOUT'


class Mission(TimestampMinIn, models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.PROTECT)
    playbook = models.CharField(max_length=64)
    state = models.IntegerField(choices=MissionState.choices, default=MissionState.PENDING)
    output = models.TextField(null=True)
    commit = models.CharField(max_length=64, null=True)

    class Meta:
        ordering = ["-created_at"]


class Authorization(TimestampMinIn, models.Model):
    token = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expired_at = models.DateTimeField(null=False)

    class Meta:
        index_together = [["token", "expired_at"]]
