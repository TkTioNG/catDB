from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .serializers import (BreedSerializer, CatSerializer,
                          HomeSerializer, HumanSerializer)
from .models import Breed, Cat, Home, Human


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
