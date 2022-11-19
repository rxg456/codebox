import pathlib
import threading
from datetime import datetime

from ansible_runner.interface import run
from django.conf import settings
from django.utils import timezone
from git import Repo

from .models import Mission, MissionState, MissionEvent


class Runner:
    def __init__(self, model: Mission):
        self.model = model
        self.workdir = pathlib.Path(settings.IAC_WORKDIR, str(self.model.id))

    def on_event(self, event: MissionEvent):
        # {
        #     "uuid": "fc3ac25c-a160-4cbf-84d8-c1d4219523ce",
        #     "counter": 10,
        #     "stdout": "",
        #     "start_line": 10,
        #     "end_line": 10,
        #     "runner_ident": "43d3bee7-3ee6-44b1-9e7c-d55f660f3bff",
        #     "event": "runner_on_start",
        #     "pid": 86976,
        #     "created": "2022-11-12T12:48:35.473079",
        #     "parent_uuid": "acde4800-1122-b4bc-5568-000000000009",
        #     "event_data": {
        #         "playbook": "playbook.yaml",
        #         "playbook_uuid": "c463e94c-953d-4036-bfcd-d22ea26c89e8",
        #         "play": "demo",
        #         "play_uuid": "acde4800-1122-b4bc-5568-000000000006",
        #         "play_pattern": "virtualmachines",
        #         "task": "Print message",
        #         "task_uuid": "acde4800-1122-b4bc-5568-000000000009",
        #         "task_action": "ansible.builtin.debug",
        #         "resolved_action": "ansible.builtin.debug",
        #         "task_args": "",
        #         "task_path": "/private/tmp/codebox/30/project/playbook.yaml:6",
        #         "host": "121.36.50.10",
        #         "uuid": "fc3ac25c-a160-4cbf-84d8-c1d4219523ce"
        #     }
        # }
        if event["event"].startswith("runner_on"):
            uuid = event["parent_uuid"]
            data = event["event_data"]
            host = data['host']
            try:
                model = MissionEvent.objects.filter(uuid=uuid, host=host).get()
            except MissionEvent.DoesNotExist:
                model = MissionEvent()
            model.uuid = uuid
            model.mission = self.model
            model.state = event["event"].removeprefix("runner_on_")
            model.play = data["play"]
            model.play_pattern = data["play_pattern"]
            model.task = data["task"]
            model.task_action = data["task_action"]
            model.task_args = data["task_args"]
            model.host = host
            model.res = data.get("res", {})
            dt = data.get("start")
            if dt:
                model.start = timezone.make_aware(datetime.fromisoformat(dt))
            dt = data.get("end")
            if dt:
                model.end = timezone.make_aware(datetime.fromisoformat(dt))
            model.duration = data.get("duration")
            model.changed = data.get("res", {}).get("changed", False)
            model.save()

    def on_status(self, status: dict, runner_config):
        match status['status']:
            case "starting" | "running":
                self.model.state = MissionState.RUNNING
            case "canceled":
                self.model.state = MissionState.CANCELED
            case "timeout":
                self.model.state = MissionState.TIMEOUT
            case "failed":
                self.model.state = MissionState.FAILED
            case "successful":
                self.model.state = MissionState.COMPLETED
        self.model.save()

    def prepare(self):
        self.workdir.mkdir(parents=True)
        repo = Repo.clone_from(url=self.model.repository.url, to_path=self.workdir)
        if self.model.inventories:
            with open(self.workdir.joinpath("inventory/hosts"), 'w') as writer:
                writer.write(self.model.inventories)
        self.model.commit = repo.head.commit.hexsha

    @classmethod
    def cancel(cls, mission: Mission):
        if mission.state == MissionState.RUNNING or mission.state == MissionState.PENDING:
            mission.state = MissionState.CANCELING
            mission.save()

    def is_canceled(self):
        return Mission.objects.get(id=self.model.id).state == MissionState.CANCELING

    def exec(self):
        try:
            self.prepare()
            runner = run(private_data_dir=self.workdir,
                         playbook=self.model.playbook,
                         event_handler=self.on_event,
                         status_handler=self.on_status,
                         cancel_callback=self.is_canceled
                         )
            self.model.output = runner.stdout.read()
        except Exception as e:
            print(e)
            self.model.state = MissionState.FAILED
        finally:
            self.model.save()

    def run(self):
        t = threading.Thread(target=self.exec)
        t.daemon = True
        t.start()
