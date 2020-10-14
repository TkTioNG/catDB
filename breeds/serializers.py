from rest_framework import serializers
from .models import Breed, Cat, Home, Human


class HomeSerializer(serializers.HyperlinkedModelSerializer):
    """
    docstring
    """
    # ['id', 'name', 'address', 'hometype']
    url = serializers.HyperlinkedIdentityField(view_name="breeds:home-detail")

    class Meta:
        model = Home
        fields = '__all__'


class BreedSerializer(serializers.HyperlinkedModelSerializer):
    """
    docstring
    """
    url = serializers.HyperlinkedIdentityField(view_name="breeds:breed-detail")

    class Meta:
        model = Breed
        fields = '__all__'


class HumanSerializer(serializers.HyperlinkedModelSerializer):
    """
    docstring
    """
    url = serializers.HyperlinkedIdentityField(view_name="breeds:human-detail")
    home = serializers.HyperlinkedRelatedField(
        view_name='breeds:home-detail',
        queryset=Home.objects.all()
    )

    class Meta:
        model = Human
        fields = '__all__'


class CatSerializer(serializers.HyperlinkedModelSerializer):
    """
    docstring
    """
    url = serializers.HyperlinkedIdentityField(view_name="breeds:cat-detail")
    breed = serializers.HyperlinkedRelatedField(
        view_name="breeds:breed-detail",
        queryset=Breed.objects.all()
    )
    owner = serializers.HyperlinkedRelatedField(
        view_name="breeds:human-detail",
        queryset=Human.objects.all()
    )

    class Meta:
        model = Cat
        fields = '__all__'
