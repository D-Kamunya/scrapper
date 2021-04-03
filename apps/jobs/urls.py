from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, include

app_name = "jobs"

router = DefaultRouter()

router.register(r'jobs', views.JobsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
