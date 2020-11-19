import string
import random
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token

BASE_URL = "http://testserver"
VALID_USERNAME = "Human 1"
VALID_EMAIL = "email@testing.com"


def create_token():
    # Create a valid token
    user = User.objects.create(username=VALID_USERNAME,
                               password=VALID_USERNAME,
                               email=VALID_EMAIL)
    token = Token.objects.create(user=user)
    return token


def get_token_key_header(key):
    # Format token key into WWW-Authentication format
    return "Token {}".format(key)


def get_valid_token_key():
    valid_token = create_token()
    return get_token_key_header(valid_token.key)


def get_expired_token_key():
    expired_token = create_token()
    # Expiring the token manually
    expired_token.created = timezone.now() \
        - timedelta(hours=settings.AUTH_TOKEN_EXPIRING_HOURS, seconds=1)
    expired_token.save()
    return get_token_key_header(expired_token.key)


def get_invalid_token_key():
    # token is made up of 40 lowercase alphanumeric characters
    invalid_token_key = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=40)
    )
    return get_token_key_header(invalid_token_key)


def get_data_from_json(json_data, *args):
    return {arg: json_data.get(arg, None) for arg in args}

# TODO: Add negative test case


class BaseTestCase(APITestCase):
    '''
    Base Test Case Template that provide `add (POST)`, `remove (DELETE)`, 
    `modify (PUT)`, `partial modify (PATCH)`, `retrieve (GET)` function.


    Test Case Code Format: #T$$-X00

    Where
    =====
        $$: BV - Breed ViewSet Test Cases
            CV - Cat ViewSet Test Cases
            HV - Home ViewSet Test Cases
            PV - Human ViewSet Test Cases

        X:  A - Add (POST)
            M - Modify (PUT)
            P - Partial Modify (PATCH)
            D - Remove (DELETE)
            R - Retrieve (GET)

    '''

    def login_with_token(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=token)

    def add_obj(self, url, data, token=None):
        if token:
            self.login_with_token(token)
        response = self.client.post(reverse(url), data=data)
        return response

    def remove_obj(self, url, data, pk, token=None):
        if token:
            self.login_with_token(token)
        response = self.client.delete(reverse(url, args=[pk]), data=data)
        return response

    def modify_obj(self, url, data, pk, token=None):
        if token:
            self.login_with_token(token)
        response = self.client.put(reverse(url, args=[pk]), data=data)
        return response

    def partial_modify_obj(self, url, data, pk, token=None):
        if token:
            self.login_with_token(token)
        response = self.client.patch(reverse(url, args=[pk]), data=data)
        return response

    def retrieve_obj(self, url, pk=None, data=None, token=None):
        if token:
            self.login_with_token(token)
        if pk:
            response = self.client.get(reverse(url, args=[pk]), data=data)
        else:
            response = self.client.get(reverse(url), data=data)
        return response

    def get_num_of_obj(self, list_view_name):
        self.client.logout()
        response = self.client.get(reverse(list_view_name))
        return response.json()['count']

    class Meta:
        abstract = True
