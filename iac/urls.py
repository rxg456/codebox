from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MissionViewSet, RepositoryViewSet

router = DefaultRouter()
router.register(r'mission', MissionViewSet, basename="mission")
router.register(r'repository', RepositoryViewSet, basename="repository")

urlpatterns = [
    path('', include(router.urls)),
]
