from django.db import models


class Gender(models.TextChoices):
    MALE = ('M', 'Male')
    FEMALE = ('F', 'Female')
    OTHER = ('O', 'Other')


class Home(models.Model):
    """
    House of a person.
    name: Name of the house? TODO: to be confirm
    address: address of the house.
    type: type of the house (landed|condominium)
    """
    pass


class Breed(models.Model):
    """
    Type of the cat breed.
    name - PK: Name of the breed.
    origin: Origin of the cat breed.
    description: description on the cat breed.
    """
    name = models.CharField(max_length=30)
    origin = models.CharField(max_length=30)
    description = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Human(models.Model):
    """
    People who breed a cat.
    name: Name of the person.
    gender: gender of the person.
    date_of_birth: birth date of the person.
    home - FK: house of the person.
    """
    name = models.CharField(max_length=30)
    gender = models.CharField(
        max_length=1, choices=Gender.choices, default=Gender.OTHER)
    date_of_birth = models.DateTimeField(auto_now_add=True)
    home = models.ForeignKey('Home', on_delete=models.CASCADE)


class Cat(models.Model):
    """
    Cat.
    name: Name of the cat.
    gender: gender of the cat.
    date_of_birth: birth date of the cat
    breed - FK: Type of the cat breed
    owner - FK: Owner to the cat
    """
    name = models.CharField(max_length=30)
    gender = models.CharField(
        max_length=1, choices=Gender.choices, default=Gender.OTHER)
    date_of_birth = models.DateTimeField(auto_now_add=True)
    breed = models.ForeignKey('Breed', related_name='cats', on_delete=models.CASCADE)
    owner = models.ForeignKey('Human', related_name='cats', on_delete=models.CASCADE)
