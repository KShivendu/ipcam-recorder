from recorder.tasks import record_stream_task
from django.contrib.auth.models import User
from recorder.serializers import RecorderSerializer
from recorder.models import Recorder
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views import View
import threading
from utils import random_str, validate_serializer
import logging
from django.db.models import Q

from recorder.serializers import UserSerializer

from rest_framework import viewsets, permissions


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


threads = []

logging.basicConfig(level=logging.DEBUG)


def process_path(filepath):
    # TODO SECURITY
    return filepath


def process_url(url):
    # TODO SECURITY
    return url


class RecorderController(View):
    # @validate_serializer(RecorderSerializer)
    def post(self, request):
        data = request.POST
        logging.info("DATA : " + str(data))
        url = process_url(data['url'])

        foldername = process_path(data['folder'])

        recorder = Recorder(
            stream_url=url, foldername=foldername)  # , thread_index=len(threads))
        recorder.save()

        record_stream_task.delay(recorder.id)

        # thread = threading.Thread(
        #     target=record_stream, args=(recorder.id,))
        # threads.append(thread)
        # thread.start()
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
            # stop_thread -> this func doesn't exist
            threads[index].stop_thread()
        except Exception as e:
            logging.error(e)
            return JsonResponse({'status': 'ERROR'})
