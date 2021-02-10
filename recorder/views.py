from uuid import uuid4
from celery import uuid
from recorder.tasks import record_stream_task
from django.contrib.auth.models import User
from recorder.serializers import RecorderSerializer
from recorder.models import Recorder, Recording
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views import View
import threading
from utils import random_str, validate_serializer
import logging
from django.db.models import Q
from recorder.serializers import UserSerializer
from rest_framework import viewsets, permissions
from celery.result import AsyncResult
from cam_recorder.celery import app as celery_app
from cv2 import cv2
import json
from django.utils.timezone import now
from celery.contrib.abortable import AbortableAsyncResult


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


logging.basicConfig(level=logging.DEBUG)


def process_path(filepath):
    # TODO SECURITY
    return filepath


def process_urls(urls):
    # TODO SECURITY
    return urls[0]


def process_active_hours(time):
    # TODO SECURITY
    return time


class RecorderController(View):
    # @validate_serializer(RecorderSerializer)
    def post(self, request):
        # Retrive data from request
        data = json.loads(request.body)  # request.POST
        logging.info("DATA : " + str(data))

        # Process data
        url = process_urls(data['urls'])
        foldername = process_path(data['folder'])
        active_hours = process_active_hours(data['activeHours'])

        # Store and start recorder
        id = uuid4()
        recorder = Recorder(
            id=id,
            url=url,
            folder=foldername,
            task_id=id
        )
        recorder.save()
        recording = Recording(id=id, recorder=recorder)
        recording.save()

        # Start task
        record_stream_task.apply_async(task_id=str(id))

        return HttpResponse(str(recorder.id))

    def get_recorder_state(self, recorder):
        result = AbortableAsyncResult(str(recorder.task_id))
        state = result.state

        return {
            "id": recorder.id,
            'url': recorder.url,
            'folder': recorder.folder,
            'status': state,
            'created_at': recorder.created_at
        }

    def get(self, request):
        data = request.GET
        if 'id' in data:
            id = data['id']
            try:
                recorder = Recorder.objects.get(id=id)
                return JsonResponse({'status': [self.get_recorder_state(recorder)]})
            except Recorder.DoesNotExist:
                return JsonResponse({'status': []})

        response = []

        recorders = []
        if 'showInactive' in data:
            recorders = Recorder.objects.all()
        else:
            recorders = Recorder.objects.filter(~Q(status=0))

        for recorder in recorders:
            recorder_state = self.get_recorder_state(recorder)
            response.append(recorder_state)

        return JsonResponse({'status': response})

    def delete(self, request):
        if 'id' in request.GET:
            id = request.GET['id']
            try:
                recorder = Recorder.objects.get(id=id)
                # result = celery_app.control.abort()
                abortable_task = AbortableAsyncResult(str(recorder.task_id))
                result = abortable_task.abort()
                # revoke(recorder.task_id, signal='SIGINT', terminate=True)
                print("REVOKE STATUS =", result)
                recorder_state = self.get_recorder_state(recorder)
                if recorder_state['status'] == 'ABORTED':
                    recording = Recording.objects.get(recorder=recorder)
                    recording.active = False
                    recording.end_time = now()
                    recording.save(update_fields=['active'])

                    recorder.status = 0  # STOPPED
                    recorder.save(update_fields=['status'])

                return JsonResponse({'status': [recorder_state]})
            except Recorder.DoesNotExist:
                return JsonResponse({"status": "DOESN'T EXIST"})
            except Exception as e:
                logging.error(e)
                recorder = Recorder.objects.get(id=id)
                return JsonResponse({'status': [self.get_recorder_state(recorder)]})

        return JsonResponse({'status': []})  # ERROR


class RecordingController(View):

    def is_file_good(self, filepath):
        try:
            vid = cv2.VideoCapture(filepath)
            if not vid.isOpened():
                raise NameError('Video can\'t be opened')
        except cv2.error as e:
            print("cv2.error:", e)
            return False
        except Exception as e:
            print("Exception:", e)
            return False
        else:
            print("no problem reported")
            return True

    def get_file_info(self, recording):
        status = self.is_file_good(recording.filepath)
        return {
            'id': str(recording.id),
            'filepath': recording.filepath,
            'health': 'PLAYABLE' if status else 'CORRUPT',
            'url': recording.url,
            'is_recording': recording.active,
            'start_time': recording.start_time,
            'end_time': recording.end_time,
        }

    def get(self, request):
        data = request.GET
        if 'id' in data:
            try:
                recording = Recording.objects.get(id=id)
                return JsonResponse(
                    {'results': [self.get_file_info(recording)]})
            except Recorder.DoesNotExist:
                return JsonResponse({'results': []})

        recordings = Recording.objects.all()

        response = []
        for recording in recordings:
            response.append(self.get_file_info(recording))

        return JsonResponse({'results': response})
