from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Breed, Cat, Home, Human


class HomeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="breeds:home-detail")

    class Meta:
        model = Home
        fields = '__all__'


class BreedSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="breeds:breed-detail")
    cats = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='breeds:cat-detail'
    )
    # Customize the method field to produce a list of hyperlinks
    # to the Home model through the cat's owner (Human model)
    homes = serializers.SerializerMethodField('get_breed_homes')

    def get_breed_homes(self, obj):
        # Retrieving all unique owners whose cat's is the current breed type
        all_owners = Cat.objects.filter(breed=obj.id).values_list(
            'owner', flat=True).distinct()
        # Retrieving all unique home among the owners
        homes = set(Home.objects.filter(
            human__id__in=all_owners).values_list('id', flat=True))
        # Convert the retrieved home ids into hyperlinks
        result = [
            reverse('breeds:home-detail',
                    args=[home_id], request=self.context['request'])
            for home_id in homes
        ]
        return result

    class Meta:
        model = Breed
        fields = '__all__'


class HumanSerializer(serializers.HyperlinkedModelSerializer):
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
    Expose home of the cat in the serializer
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
    # Customize the method field to produce a hyperlink to the Home model
    # through the cat's owner (Human model)
    home = serializers.SerializerMethodField('get_cat_home')

    def get_cat_home(self, obj):
        # Assume that the Cat-Human is Many-to-One relationship
        # and Human-Home is Many-to-One relationship, hence one cat
        # will only has one home related to it
        cat_home = Human.objects.get(id=obj.owner_id).home_id
        result = reverse('breeds:home-detail',
                         args=[cat_home], request=self.context['request'])
        return result

    class Meta:
        model = Cat
        fields = '__all__'
