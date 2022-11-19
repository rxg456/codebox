from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MissionViewSet, RepositoryViewSet, AuthorizationViewSet, PeriodicMissionViewSet

router = DefaultRouter()
router.register(r'mission', MissionViewSet, basename="mission")
router.register(r'repository', RepositoryViewSet, basename="repository")
router.register(r'auth', AuthorizationViewSet, basename="auth")
router.register(r'schedule', PeriodicMissionViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
]
