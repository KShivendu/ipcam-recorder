from recorder.models import Recorder
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views import View
import threading
from utils import random_str
import logging
from django.db.models import Q


threads = []

logging.basicConfig(level=logging.DEBUG)


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


def process_path(filepath):
    # TODO SECURITY
    return filepath


def process_url(url):
    # TODO SECURITY
    return url


class RecorderController(View):
    def post(self, request):
        data = request.POST
        print("DATA : ", data)
        logging.info("DATA : ", data)
        url = process_url(data['url'])

        foldername = process_path(data['folder'])

        recorder = Recorder(
            stream_url=url, foldername=foldername, thread_index=len(threads))
        recorder.save()

        thread = threading.Thread(
            target=record_stream, args=(recorder.id,))
        threads.append(thread)
        thread.start()
        return HttpResponse(recorder.id)

    def get(self, request):
        print("THREADS =", threads)
        data = request.GET
        if 'id' in data:
            uuid = data['id']
            try:
                status = Recorder.objects.get(id=uuid).status
                return JsonResponse({'status': [{uuid: status}]})
            except Recorder.DoesNotExist:
                return JsonResponse({'status': [{uuid: -1}]})

        response = []
        # List only active threads - recording or crashed
        recorders = Recorder.objects.filter(Q(status=1) | Q(status=2))
        print("RECORDERS : ", recorders)

        for recorder in recorders:
            if recorder.thread_index < len(threads):
                thread = threads[recorder.thread_index]
                print("Thread =", thread)
            response.append({str(recorder.id): recorder.status})
        return JsonResponse({'status': response})

    def delete(self, request):
        uuid = request.GET['uuid']
        try:
            recorder = Recorder.objects.get(id=uuid)
            index = recorder.thread_index
            print("THREAD INDEX =", index)
            threads[index].stop_thread()
        except Exception as e:
            logging.error(e)
            return JsonResponse({'status': 'ERROR'})
