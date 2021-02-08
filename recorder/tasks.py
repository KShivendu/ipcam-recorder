from recorder.models import Recorder
from celery.decorators import task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


def record_stream(recorder_id):
    recorder = Recorder.objects.get(id=recorder_id)
    index = recorder.thread_index
    try:
        while True:
            # JUST WASTE TIME
            pass
    except:
        recorder.status = -1  # MEANS SOMETHING WENT WRONG WITH RECORDING
        recorder.save(update_fields=['status'])

    # logging.info('SOMETHING')
    # from cv2 import cv2
    # vcap = cv2.VideoCapture(url)
    # fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    # out = cv2.VideoWriter(f'data/{uuid}.mp4', fourcc, 20.0, (640, 480))

    # import time
    # import random
    # time.sleep(20)

    # while(1):
    #     flag, frame = vcap.read()
    #     out.write(frame)
    #     # CHANGES REQUIRED HERE FOR LIVESTREAM
    #     if flag or threads[index][2] != 'RECORDING':
    #         threads[index][2] = 'INACTIVE'
    #         break
    #     cv2.waitKey(1)


@task(name="record_stream_task")
def record_stream_task(recorder_id):
    """
    Starts a recording
    """
    print(f"Starting a recording task with id = {recorder_id}")
    recorder = Recorder.objects.get(id=recorder_id)
    try:
        while True:
            pass
    except:
        recorder.status = -1
        recorder.save(update_fields=['status'])


# @periodic_task(run_every=(crontab(minute='*/15')), name="some_task", ignore_result=True)
# def some_task():
    # do something

    # record_stream_task.delay('XYZ.com/stream', 'uuuid@#SX' )
