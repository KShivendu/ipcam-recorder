import logging
from celery.exceptions import Ignore
from typing_extensions import final
from recorder.models import Recorder, Recording
from celery.decorators import task, periodic_task
# from celery.task.schedules import crontab
from celery.utils.log import get_task_logger
from django.utils.timezone import now
import cv2
from celery import states


from celery.contrib.abortable import AbortableTask


logger = get_task_logger(__name__)


@task(bind=True)
def hello_world(self):
    print('Hello world!')


# @periodic_task(run_every=crontab(hour=7, minute=30, day_of_week="mon"))
# def every_monday_morning():
#     print("This runs every Monday morning at 7:30a.m.")


@task(name="record_stream_task", bind=True, base=AbortableTask)
def record_stream_task(self):
    """
    Starts a recording
    """

    recorder_id = record_stream_task.request.id  # get the task id for current task
    self.update_state(state='STARTING', meta={'id': recorder_id})

    logging.info(f"Starting a recording task with id = {recorder_id}")
    recorder = Recorder.objects.get(id=recorder_id)
    filepath = recorder.filepath  # .replace(".mp4", ".avi")
    logging.info(f"Save location : {filepath}")
    logging.info(f"URL : {recorder.url}")

    recorder = Recorder.objects.get(id=recorder_id)
    import os
    os.makedirs(f'data/{recorder.folder}', exist_ok=True)
    try:
        vcap = cv2.VideoCapture(recorder.url)
        fw = int(vcap.get(3))
        fh = int(vcap.get(4))
        out = cv2.VideoWriter(recorder.filepath,
                              cv2.VideoWriter_fourcc(*'MP4V'), 20.0, (fw, fh))
        if vcap.isOpened():
            self.update_state(state='RECORDING', meta={'id': recorder_id})

        while vcap.isOpened():
            flag, frame = vcap.read()
            if flag:
                out.write(frame)
            else:
                raise Exception("Something went wrong with the source.")

            if self.is_aborted():
                raise Exception("Aborted")

        if not vcap.isOpened():
            raise Exception("Source isn't streaming.")

    except Exception as e:
        logging.error(f"ERROR : {e}")

        recording = Recording.objects.get(recorder=recorder)
        recording.end_time = now()
        recording.save(update_fields=['end_time'])
        recorder.status = -1
        recorder.save(update_fields=['status'])
        logging.info("EXITING")

        if self.is_aborted():
            self.update_state(state='STOPPED', meta={'info': str(e)})
        else:
            self.update_state(state='CRASHED', meta={'info': str(e)})
        raise Ignore()

    # import os
    # os.makedirs(f'data/{recorder.folder}', exist_ok=True)
    # with open(recorder.filepath, 'w+') as f:
    #     f.write('SOME TEXT')


# @periodic_task(run_every=(crontab(minute='*/15')), name="some_task", ignore_result=True)
# def some_task():
    # do something

    # record_stream_task.delay('XYZ.com/stream', 'uuuid@#SX' )
