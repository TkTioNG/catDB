from django.db import models
from django.utils import timezone
from django.core.validators import ValidationError


def date_in_past(date):
    today = timezone.now().date()
    if date > today:
        raise ValidationError(
            "Date of birth should be in the past, which is before %(today)s.",
            params={'today': today},
        )


class Gender(models.TextChoices):
    MALE = ('M', 'Male')
    FEMALE = ('F', 'Female')
    OTHER = ('O', 'Other')


class Home(models.Model):
    """
    House of a person.
    name: Name of the house? TODO: to be confirm
    address: address of the house.
    hometype: type of the house (landed|condominium)
    """
    class HomeType(models.TextChoices):
        LANDED = 'landed'
        CONDOMINIUM = 'condominium'

    name = models.CharField(max_length=30)
    address = models.CharField(max_length=300)
    hometype = models.CharField(max_length=11, choices=HomeType.choices)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        db_table = "%s_%s" % ("catapp", "home")


class Breed(models.Model):
    """
    Type of the cat breed.
    name - PK: Name of the breed.
    origin: Origin of the cat breed.
    description: description on the cat breed.
    """
    name = models.CharField(max_length=30, unique=True)
    origin = models.CharField(max_length=30)
    description = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        db_table = "%s_%s" % ("catapp", "breed")


class Human(models.Model):
    """
    People who breed a cat.
    name: Name of the person.
    gender: gender of the person.
    date_of_birth: birth date of the person.
    description: Description of the person.
    home - FK: house of the person.
    """
    name = models.CharField(max_length=30)
    gender = models.CharField(
        max_length=1, choices=Gender.choices, default=Gender.OTHER
    )
    date_of_birth = models.DateField(validators=[date_in_past])
    description = models.CharField(max_length=300, blank=True)
    home = models.ForeignKey('Home', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        db_table = "%s_%s" % ("catapp", "human")


class Cat(models.Model):
    """
    Cat.
    name: Name of the cat.
    gender: gender of the cat.
    date_of_birth: birth date of the cat
    description: description on the cat
    breed - FK: Type of the cat breed
    owner - FK: Owner to the cat
    """
    name = models.CharField(max_length=30)
    gender = models.CharField(
        max_length=1, choices=Gender.choices, default=Gender.OTHER)
    date_of_birth = models.DateField(validators=[date_in_past])
    description = models.CharField(max_length=300, blank=True)
    breed = models.ForeignKey(
        'Breed', related_name='cats', on_delete=models.CASCADE)
    owner = models.ForeignKey(
        'Human', related_name='cats', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        db_table = "%s_%s" % ("catapp", "cat")
