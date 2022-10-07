from django.db import models


class TimestampMibIn(models.Model):
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


class Mission(TimestampMibIn, models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.PROTECT)
    playbook = models.CharField(max_length=64)
    state = models.IntegerField(choices=MissionState.choices, default=MissionState.PENDING)
    output = models.TextField(null=True)
    commit = models.CharField(max_length=64, null=True)
