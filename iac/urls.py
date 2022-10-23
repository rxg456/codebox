from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MissionViewSet, RepositoryViewSet, AuthorizationViewSet

router = DefaultRouter()
router.register(r'mission', MissionViewSet, basename="mission")
router.register(r'repository', RepositoryViewSet, basename="repository")
router.register(r'auth', AuthorizationViewSet, basename="auth")

urlpatterns = [
    path('', include(router.urls)),
]
