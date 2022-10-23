import pathlib
import threading

from ansible_runner.interface import run
from django.conf import settings
from git import Repo

from .models import Mission, MissionState


class Runner:
    def __init__(self, model: Mission):
        self.model = model
        self.workdir = pathlib.Path(settings.IAC_WORKDIR, str(self.model.id))

    def prepare(self):
        self.workdir.mkdir(parents=True)
        repo = Repo.clone_from(url=self.model.repository.url, to_path=self.workdir)
        self.model.commit = repo.head.commit.hexsha
        self.model.state = MissionState.RUNNING
        self.model.save()

    def exec(self):
        self.model.state = MissionState.PENDING
        self.model.save()
        try:
            self.prepare()
            runner = run(private_data_dir=self.workdir, playbook=self.model.playbook)
            if runner.rc == 0:
                self.model.state = MissionState.COMPLETED
            self.model.output = runner.stdout.read()
        except:
            self.model.state = MissionState.FAILED
        finally:
            self.model.save()

    def run(self):
        t = threading.Thread(target=self.exec)
        t.daemon = True
        t.start()
