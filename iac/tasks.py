from celery import shared_task

from .models import Mission
from .runner import Runner


@shared_task
def execute(mission_id):
    mission = Mission.objects.get(id=mission_id)
    runner = Runner(mission)
    runner.exec()
