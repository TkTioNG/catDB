import factory
import datetime

from .models import Breed, Cat, Home, Human, Gender


class HomeFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Home

    name = factory.Sequence(lambda n: "Home %d" % n)
    address = factory.Faker('address')
    hometype = factory.Iterator(Home.HomeType.choices, getter=lambda c: c[0])

    @classmethod
    def _setup_next_sequence(cls):
        try:
            return Home.objects.latest('id').id + 1
        except Home.DoesNotExist:
            return 1

class BreedFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Breed

    name = factory.Sequence(lambda n: "Breed %d" % n)
    origin = factory.Faker('country')
    description = factory.Faker('text')
    
    @classmethod
    def _setup_next_sequence(cls):
        try:
            return Breed.objects.latest('id').id + 1
        except Breed.DoesNotExist:
            return 1


class HumanFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Human

    name = factory.Faker('name')
    gender = factory.Iterator(Gender.choices, getter=lambda c: c[0])
    date_of_birth = factory.Faker('date_between_dates',
        date_start=datetime.date(1990, 1, 1),
        date_end=datetime.date(2010, 10, 18),
    )
    description = factory.Faker('text')
    home = factory.SubFactory(HomeFactory)
    

class CatFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = Cat
        
    name = factory.Faker('name')
    gender = factory.Iterator(Gender.choices, getter=lambda c: c[0])
    date_of_birth = factory.Faker('date_between_dates',
        date_start=datetime.date(2008, 1, 1),
        date_end=datetime.date(2020, 5, 31),
    )
    description = factory.Faker('text')
    breed = factory.SubFactory(BreedFactory) 
    owner = factory.SubFactory(HumanFactory)
