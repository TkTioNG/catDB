from datetime import timedelta
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from catapp.serializers import (BreedSerializer, CatSerializer,
                                HomeSerializer, HumanSerializer)
from catapp.models import Breed, Cat, Home, Human
from catapp.authentication import EXPIRING_HOUR


class HomeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Home.objects.all()
    serializer_class = HomeSerializer
    filterset_fields = '__all__'
    search_fields = ['name', 'address']


class BreedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    filterset_fields = '__all__'
    search_fields = ['name', 'origin']


class HumanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Human.objects.all()
    serializer_class = HumanSerializer
    filterset_fields = '__all__'
    search_fields = ['name', 'gender', 'date_of_birth']


class CatViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    filterset_fields = '__all__'
    search_fields = ['name', 'gender', 'date_of_birth']


class ObtainNewAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)

            now = timezone.now()
            if not created and now - token.created > timedelta(hours=EXPIRING_HOUR):
                token.delete()
                token = Token.objects.create(user=user)
                token.created = now
                token.save()

            return Response({'token': token.key})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
