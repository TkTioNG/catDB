from rest_framework import serializers
from rest_framework.reverse import reverse
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
    cats = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='breeds:cat-detail'
    )
    homes = serializers.SerializerMethodField('get_breed_homes')

    def get_breed_homes(self, obj):
        all_owners = Cat.objects.filter(breed=obj.id).values_list(
            'owner', flat=True).distinct()
        homes = list(Home.objects.filter(
            human__id__in=all_owners).values_list('id', flat=True))
        result = [
            "{}".format(reverse('breeds:home-detail',
                                args=[home_id], request=self.context['request']))
            for home_id in homes
        ]
        return result

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
    cats = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='breeds:cat-detail',
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
    '''
    home = serializers.HyperlinkedRelatedField(
        view_name='breeds:home-detail',
        read_only=True
    )
    '''
    home = serializers.SerializerMethodField('get_cat_home')

    def get_cat_home(self, obj):
        cat_home = Human.objects.get(id=obj.owner_id).home_id
        result = "{}".format(
            reverse('breeds:home-detail',
                    args=[cat_home],
                    request=self.context['request'])
        )
        return result

    class Meta:
        model = Cat
        fields = '__all__'
