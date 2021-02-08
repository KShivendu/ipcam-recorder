from django.db import models
import uuid
# Create your models here.


class Recorder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stream_url = models.CharField(max_length=256, default='demo.mp4')
    foldername = models.CharField(max_length=64, default='tmp')
    # -1 -> DOESN'T EXIST, 0 -> STOPPED, 1 -> RECORDING, 2 -> CRASHED
    status = models.IntegerField(default=1)
    thread_index = models.IntegerField(default=0)

    def __str__(self):
        return self.stream_url

    @property
    def filepath(self):
        return f'data/{self.foldername}/{self.id}.mp4'
