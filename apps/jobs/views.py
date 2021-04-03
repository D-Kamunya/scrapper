from django.shortcuts import render
from rest_framework import viewsets, generics, mixins, filters
from rest_framework.response import Response
from rest_framework import status, exceptions
from .models import Job
from .serializers import JobSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

job_title = openapi.Parameter('job_title', in_=openapi.IN_QUERY,
                              type=openapi.TYPE_STRING)
job_location = openapi.Parameter('job_location', in_=openapi.IN_QUERY,
                                 type=openapi.TYPE_STRING)


# Create your views here.
class JobsViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    # Do not change!!!
    obj_name = 'job'

    def get_queryset(self):
        qs = self.queryset
        job_title = self.request.query_params.get('job_title', None)
        job_location = self.request.query_params.get('job_location', None)

        if job_title:
            qs = qs.filter(title__icontains=job_title)
        if job_location:
            qs = qs.filter(location__icontains=job_location)
        return qs

    @swagger_auto_schema(
        operation_description="Search a job by job title,job location,both or leave params empty to get all jobs",
        manual_parameters=[job_title, job_location],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = JobSerializer(queryset, many=True)
        return Response(serializer.data)
