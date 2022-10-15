from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Mission, Repository
from .runner import Runner
from .serializers import MissionSerializer, MissionCreationSerializer, RepositorySerializer, \
    RepositoryCreationSerializer, RepositoryMutationSerializer


@extend_schema(tags=["IacRepository"])
class RepositoryViewSet(GenericViewSet):
    queryset = Repository.objects.all().order_by("id")
    serializer_class = RepositorySerializer

    @extend_schema("createRepository", request=RepositoryCreationSerializer,
                   responses=RepositorySerializer)
    def create(self, request, *args, **kwargs):
        serializer = RepositoryCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(RepositorySerializer(serializer.instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema("listRepositories", responses=RepositorySerializer(many=True))
    def list(self, request, *args, **kwargs):
        res = self.paginate_queryset(self.queryset)
        serializer = RepositorySerializer(res, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema("getRepository", responses=RepositorySerializer)
    def retrieve(self, request, *args, **kwargs):
        serializer = RepositorySerializer(self.get_object())
        return Response(serializer.data)

    @extend_schema("updateRepository", responses=RepositorySerializer, request=RepositoryMutationSerializer)
    def update(self, request, *args, **kwargs):
        serializer = RepositoryMutationSerializer(self.get_object(), data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(RepositorySerializer(serializer.instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["IacMission"])
class MissionViewSet(GenericViewSet):
    queryset = Mission.objects.all().order_by("id")
    serializer_class = MissionSerializer

    @extend_schema("createMission", request=MissionCreationSerializer, responses=MissionSerializer)
    def create(self, request, *args, **kwargs):
        serializer = MissionCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            Runner(serializer.instance).run()
            return Response(data=MissionSerializer(serializer.instance).data)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema("listMissions", responses=MissionSerializer(many=True))
    def list(self, request, *args, **kwargs):
        res = self.paginate_queryset(self.queryset)
        serializer = MissionSerializer(instance=res, many=True)
        return self.get_paginated_response(serializer.data)

    @extend_schema("getMission", responses=MissionSerializer)
    def retrieve(self, request, *args, **kwargs):
        serializer = MissionSerializer(self.get_object())
        return Response(serializer.data)
