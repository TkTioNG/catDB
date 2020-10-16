from django.test import TestCase

from .models import Breed, Cat, Home, Human

VALID_USERNAME = "Human 1"
EXPIRED_USERNAME = "admin"


def get_valid_token():
    user = User.objects.get(username=VALID_USERNAME)
    valid_token = Token.objects.get(user=user)
    return valid_token.key


def get_expired_token():
    user = User.objects.get(username=EXPIRED_USERNAME)
    valid_token = Token.objects.get(user=user)
    return valid_token.key


def get_invalid_token():
    invalid_token = "c29f841aa4f21018ae62474a087627d3bdea353b"
    return invalid_token


class BaseTestCase(TestCase):

    def add_obj(self, *args, **kwargs):
        self.assertTrue(False, "add obj failed")

    def remove_obj(self, *args, **kwargs):
        self.assertTrue(False, "add obj failed")

    def modify_obj(self, *args, **kwargs):
        self.assertTrue(False, "add obj failed")

    def retrieve_obj(self, *args, **kwargs):
        self.assertTrue(False, "add obj failed")

    class Meta:
        abstract = True


class BreedViewSetTests(BaseTestCase):

    def test_add_breed_obj(self):
        self.add_obj()

    def test_remove_breed_obj(self):
        self.add_obj()

    def test_modify_breed_obj(self):
        self.add_obj()

    def test_retrieve_breed_obj(self):
        self.add_obj()
