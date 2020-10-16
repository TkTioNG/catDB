import string
import random
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token

from .models import Breed, Cat, Home, Human

BASE_URL = "http://127.0.0.1:8000"
VALID_USERNAME = "Human 1"
EXPIRED_USERNAME = "admin"
VALID_EMAIL = "email@testing.com"


def create_token():
    # Create a valid token
    # TODO: Modify it by returning user so that the user 
    # token can be set to expire based on the user
    user = User.objects.create(username=VALID_USERNAME,
                               password=VALID_USERNAME,
                               email=VALID_EMAIL)
    token = Token.objects.get_or_create(user=user)
    return token


def get_token_key_header(key):
    # Format token key into WWW-Authentication format
    return "Token {}".format(key)


def get_valid_token_key():
    valid_token, status = create_token()
    return get_token_key_header(valid_token.key)


def get_expired_token_key():
    # TODO: modified to obtain expired token
    # user = User.objects.get(username=EXPIRED_USERNAME)
    # expired_token = Token.objects.get(user=user)
    # return get_token_key_header(expired_token.key)
    return get_valid_token_key()


def get_invalid_token_key():
    # token is made up of 40 lowercase alphanumeric characters
    invalid_token_key = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=40)
    )
    return get_token_key_header(invalid_token_key)


class BaseTestCase(APITestCase):

    def add_obj(self, url, data, token=None):
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(reverse(url), data=data)
        return response

    def remove_obj(self, url, data, pk, token=None):
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.delete(reverse(url, args=[pk]), data=data)
        return response

    def modify_obj(self, url, data, pk, token=None):
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.put(reverse(url, args=[pk]), data=data)
        return response

    def partial_modify_obj(self, url, data, pk, token=None):
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.patch(reverse(url, args=[pk]), data=data)
        return response

    def retrieve_obj(self, url, data, pk, token=None):
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(reverse(url, args=[pk]), data=data)
        return response

    class Meta:
        abstract = True


class BreedViewSetTests(BaseTestCase):
    
    # initialise before each test case
    def setUp(self):
        self.list_url = 'breeds:breed-list'
        self.detail_url = 'breeds:breed-detail'
        self.data = {
            'name': 'test name',
            'origin': 'test origin',
            'description': 'test description',
        }
        self.new_data = {
            'name': 'new test name',
            'origin': 'new test origin',
            'description': 'new test description',
        }

    def create_breed_obj(self):
        return Breed.objects.create(
            name=self.data['name'],
            origin=self.data['origin'],
            description=self.data['description']
        )

    # test cases for adding a new breed object
    def test_add_breed_obj_with_valid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "Add breed object with valid token failed"
        )

    # def test_add_breed_obj_with_expired_token(self):
    #     self.add_obj(condition="with expired token ")

    def test_add_breed_obj_with_invalid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Able to add breed object with invalid token"
        )

    def test_add_breed_obj_without_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Able to add breed object without token"
        )

    # test cases for removing an existing breed object
    def test_remove_breed_obj_with_valid_token(self):
        breed_obj = self.create_breed_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "Remove breed object with valid token failed"
        )

    # def test_remove_breed_obj_with_expired_token(self):
    #     self.remove_obj(condition="with expired token ")

    def test_remove_breed_obj_with_invalid_token(self):
        breed_obj = self.create_breed_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Able to remove breed object with invalid token"
        )

    def test_remove_breed_obj_without_token(self):
        breed_obj = self.create_breed_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Able to remove breed object without token"
        )

    # test cases for modifying (put) an existing breed object
    def test_modify_breed_obj_with_valid_token(self):
        breed_obj = self.create_breed_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=breed_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Modify breed object with valid token failed"
        )
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'origin': json_data.get('origin', None),
            'description': json_data.get('description', None),
        }
        self.assertEqual(
            modified_data, self.new_data,
            "Breed object was not modified with valid token"
        )

    # def test_modify_breed_obj_with_expired_token(self):
    #     self.modify_obj(condition="with expired token ")

    def test_modify_breed_obj_with_invalid_token(self):
        breed_obj = self.create_breed_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Able to modify breed object with invalid token"
        )

    def test_modify_breed_obj_without_token(self):
        breed_obj = self.create_breed_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Able to modify breed object without token"
        )

    # test cases for partially modifying (patch request) an
    # existing breed object
    def test_partial_modify_breed_obj_with_valid_token(self):
        breed_obj = self.create_breed_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "partial_modify breed object with valid token failed"
        )
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'origin': json_data.get('origin', None),
            'description': json_data.get('description', None),
        }
        self.assertEqual(
            modified_data, self.data,
            "Breed object was not partially modified with valid token"
        )

    # def test_partial_modify_breed_obj_with_expired_token(self):
    #     self.partial_modify_obj(condition="with expired token ")

    def test_partial_modify_breed_obj_with_invalid_token(self):
        breed_obj = self.create_breed_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Able to partial_modify breed object with invalid token"
        )

    def test_partial_modify_breed_obj_without_token(self):
        breed_obj = self.create_breed_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "Able to partial_modify breed object without token"
        )

    # test cases for retrieving an existing breed object
    def test_retrieve_breed_obj_with_valid_token(self):
        breed_obj = self.create_breed_obj()
        response = self.retrieve_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "Retrieve one breed object failed"
        )
        json_data = response.json()
        retrieved_data = {
            'name': json_data.get('name', None),
            'origin': json_data.get('origin', None),
            'description': json_data.get('description', None),
        }
        self.assertEqual(
            retrieved_data, self.data,
            "Retrieve data is not same as the posted data"
        )
