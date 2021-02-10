from django.db import models
import uuid
# Create your models here.


class Recorder(models.Model):
    # Might not be equal to task_id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField(max_length=256, default='demo.mp4')
    folder = models.CharField(max_length=64, default='tmp')
    # 0 -> STOPPED, 1 -> RECORDING, -1 -> CRASHED
    status = models.IntegerField(default=1)
    task_id = models.UUIDField(default=uuid.uuid4, editable=True)
    created_at = models.DateTimeField(auto_now_add=True)

    schedule_start_time = models.DateTimeField(null=True)
    schedule_end_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.filepath

    @property
    def filepath(self):
        return f'data/{self.folder}/{self.task_id}.mp4'


class Recording(models.Model):
    # Recording ID = Task ID(of both Recorder and Celery Worker)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recorder = models.ForeignKey(Recorder, on_delete=models.DO_NOTHING)

    # -1 -> DOESN'T EXIST, 0 -> STOPPED, 1 -> RECORDING, 2 -> CRASHED
    # status = models.IntegerField(default=1)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)

    @property
    def filepath(self):
        return f'data/{self.recorder.folder}/{self.id}.mp4'

    @property
    def url(self):
        return self.recorder.url

    @property
    def active(self):
        return self.recorder.status
