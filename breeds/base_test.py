from django.test import TestCase


def get_valid_token():
    pass


def get_expired_token():
    pass


def get_invalid_token():
    pass


class BaseTestCase(TestCase):

    def add_obj(self, *args, **kwargs):
        pass

    def remove_obj(self, *args, **kwargs):
        pass

    def modify_obj(self, *args, **kwargs):
        pass

    def retrieve_obj(self, *args, **kwargs):
        pass
