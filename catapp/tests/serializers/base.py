
from rest_framework.test import APIRequestFactory


def make_request():
    return APIRequestFactory().get('/')
