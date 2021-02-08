from rest_framework import serializers
from django.contrib.auth.models import User
from recorder.models import Recorder


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class RecorderSerializer(serializers.ModelSerializer):
    # ADD EXTRA HERE IF YOU WANT
    class Meta:
        model = Recorder
        fields = ('__all__')


class MultipleRecorderSerializer(serializers.ModelSerializer):
    urls = serializers.JSONField()
    foldername = serializers.CharField()
