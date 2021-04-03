from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.conf import settings
from datetime import datetime, timezone
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ('__all__')
