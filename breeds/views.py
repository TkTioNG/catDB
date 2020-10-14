from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .serializers import (BreedSerializer, CatSerializer,
                          HomeSerializer, HumanSerializer)
from .models import Breed, Cat, Home, Human


def index(request):
    return HttpResponse('Hello, World.')


class HomeViewSet(viewsets.ModelViewSet):
    """
    docstring
    """
    queryset = Home.objects.all()
    serializer_class = HomeSerializer


class BreedViewSet(viewsets.ModelViewSet):
    """
    docstring
    """
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer


class HumanViewSet(viewsets.ModelViewSet):
    """
    docstring
    """
    queryset = Human.objects.all()
    serializer_class = HumanSerializer


class CatViewSet(viewsets.ModelViewSet):
    """
    docstring
    """
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
