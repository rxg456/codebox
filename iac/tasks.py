from celery import shared_task

from .models import Mission, MissionMode, PeriodicMission
from .runner import Runner


@shared_task
def execute(mission_id):
    mission = Mission.objects.get(id=mission_id)
    runner = Runner(mission)
    runner.exec()


@shared_task
def submit(task_id):
    try:
        task = PeriodicMission.objects.get(uuid=task_id)
        mission = Mission.objects.create(
            repository=task.repository,
            playbook=task.playbook,
            inventories=task.inventories,
            mode=MissionMode.PERIODIC,
            created_by=task.created_by
        )
        execute.delay(mission.id)
    except PeriodicMission.DoesNotExist:
        pass
