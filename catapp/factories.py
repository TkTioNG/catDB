import factory
import datetime
from faker import Factory

from catapp.models import Breed, Cat, Home, Human, Gender

faker = Factory.create()


class HomeFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Home

    name = factory.Sequence(lambda n: "Home %d" % n)
    # address = factory.Faker('address')
    address = factory.LazyAttribute(lambda n: faker.address()[:300])
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
    origin = factory.LazyAttribute(lambda n: faker.country()[:30])
    description = factory.Faker('text', max_nb_chars=300)

    @classmethod
    def _setup_next_sequence(cls):
        try:
            return Breed.objects.latest('id').id + 1
        except Breed.DoesNotExist:
            return 1


class HumanFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Human

    name = factory.LazyAttribute(lambda n: faker.name()[:30])
    gender = factory.Iterator(Gender.choices, getter=lambda c: c[0])
    date_of_birth = factory.Faker('date_between_dates',
                                  date_start=datetime.date(1990, 1, 1),
                                  date_end=datetime.date.today(),
                                  )
    description = factory.Faker('text', max_nb_chars=300)
    home = factory.SubFactory(HomeFactory)


class CatFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Cat

    name = factory.LazyAttribute(lambda n: faker.name()[:30])
    gender = factory.Iterator(Gender.choices, getter=lambda c: c[0])
    date_of_birth = factory.Faker('date_between_dates',
                                  date_start=datetime.date(2008, 1, 1),
                                  date_end=datetime.date(2020, 5, 31),
                                  )
    description = factory.Faker('text', max_nb_chars=300)
    breed = factory.SubFactory(BreedFactory)
    owner = factory.SubFactory(HumanFactory)
