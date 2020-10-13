from django.db import models


class Breed(models.Model):
    """
    Type of the cat breed.
    name - PK: Name of the breed.
    origin: Origin of the cat breed.
    description: description on the cat breed.
    """
    pass


class Human(models.Model):
    """
    People who breed a cat.
    name: Name of the person.
    gender: gender of the person.
    date_of_birth: birth date of the person.
    home - FK: house of the person.
    """
    pass


class Home(models.Model):
    """
    House of a person.
    name: Name of the house? TODO: to be confirm
    address: address of the house.
    type: type of the house (landed|condominium)
    """
    pass

class Cat(models.Model):
    """
    Cat.
    name: Name of the cat.
    gender: gender of the cat.
    date_of_birth: birth date of the cat
    breed - FK: Type of the cat breed
    owner - FK: Owner to the cat
    """
    pass
