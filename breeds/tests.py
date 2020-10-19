import string
import random
import factory
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token

# from .models import Breed, Cat, Home, Human
from .factories import BreedFactory, CatFactory, HomeFactory, HumanFactory
from .authentication import EXPIRING_HOUR

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
    expired_token.created = timezone.now() - timedelta(hours=EXPIRING_HOUR,
                                                       seconds=1)
    expired_token.save()
    return get_token_key_header(expired_token.key)


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


class HomeViewSetTests(BaseTestCase):
    # Test Case Code Format; #THV-000
    # Current Test Case Sequence: THV-017

    # initialise before each test case
    def setUp(self):
        self.list_url = 'breeds:home-list'
        self.detail_url = 'breeds:home-detail'
        self.data = factory.build(dict, FACTORY_CLASS=HomeFactory)
        self.new_data = factory.build(dict, FACTORY_CLASS=HomeFactory)

    def create_home_obj(self):
        return HomeFactory.create(**self.data)

    # Test cases for adding a new home object
    # Test Case: #THV-001
    def test_add_home_obj_with_valid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#THV-001: Add home object with valid token failed"
        )

    # Test Case: #THV-002
    def test_add_home_obj_with_expired_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-002: Able to add home object with expired token"
        )

    # Test Case: #THV-003
    def test_add_home_obj_with_invalid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-003: Able to add home object with invalid token"
        )

    # Test Case: #THV-004
    def test_add_home_obj_without_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-004: Able to add home object without token"
        )

    # test cases for removing an existing home object
    # Test Case: #THV-005
    def test_remove_home_obj_with_valid_token(self):
        home_obj = self.create_home_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "#THV-005: Remove home object with valid token failed"
        )

    # Test Case: #THV-006
    def test_remove_home_obj_with_expired_token(self):
        home_obj = self.create_home_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-006: Able to remove home object with expired token"
        )

    # Test Case: #THV-007
    def test_remove_home_obj_with_invalid_token(self):
        home_obj = self.create_home_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-007: Able to remove home object with invalid token"
        )

    # Test Case: #THV-008
    def test_remove_home_obj_without_token(self):
        home_obj = self.create_home_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-008: Able to remove home object without token"
        )

    # test cases for modifying (put) an existing home object
    # Test Case: #THV-009
    def test_modify_home_obj_with_valid_token(self):
        home_obj = self.create_home_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=home_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#THV-009: Modify home object with valid token failed"
        )
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'address': json_data.get('address', None),
            'hometype': json_data.get('hometype', None),
        }
        self.assertEqual(
            modified_data, self.new_data,
            "#THV-009: Home object was not modified with valid token"
        )

    # Test Case: #THV-010
    def test_modify_home_obj_with_expired_token(self):
        home_obj = self.create_home_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=home_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-010: Able to modify home object with expired token"
        )

    # Test Case: #THV-011
    def test_modify_home_obj_with_invalid_token(self):
        home_obj = self.create_home_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=home_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-011: Able to modify home object with invalid token"
        )

    # Test Case: #THV-012
    def test_modify_home_obj_without_token(self):
        home_obj = self.create_home_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=home_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-012: Able to modify home object without token"
        )

    # test cases for partially modifying (patch request) an
    # existing home object
    # Test Case: #THV-013
    def test_partial_modify_home_obj_with_valid_token(self):
        home_obj = self.create_home_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#THV-013: partial_modify Home object with valid token failed"
        )
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'address': json_data.get('address', None),
            'hometype': json_data.get('hometype', None),
        }
        self.assertEqual(
            modified_data, self.data,
            "#THV-013: Home object was not partially modified with valid token"
        )

    # Test Case: #THV-014
    def test_partial_modify_home_obj_with_expired_token(self):
        home_obj = self.create_home_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-014: Able to partial_modify home object with expired token"
        )

    # Test Case: #THV-015
    def test_partial_modify_home_obj_with_invalid_token(self):
        home_obj = self.create_home_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-015: Able to partial_modify home object with invalid token"
        )

    # Test Case: #THV-016
    def test_partial_modify_home_obj_without_token(self):
        home_obj = self.create_home_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-016: Able to partial_modify home object without token"
        )

    # test cases for retrieving an existing home object
    # Test Case: #THV-017
    def test_retrieve_home_obj_with_valid_token(self):
        home_obj = self.create_home_obj()
        response = self.retrieve_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#THV-017: Retrieve one home object failed"
        )
        json_data = response.json()
        retrieved_data = {
            'name': json_data.get('name', None),
            'address': json_data.get('address', None),
            'hometype': json_data.get('hometype', None),
        }
        self.assertEqual(
            retrieved_data, self.data,
            "#THV-017: Retrieve data is not same as the posted data"
        )


class BreedViewSetTests(BaseTestCase):
    # Test Case Code Format; #TBV-000
    # Current Test Case Sequence: TBV-017

    # initialise before each test case
    def setUp(self):
        self.list_url = 'breeds:breed-list'
        self.detail_url = 'breeds:breed-detail'
        self.data = factory.build(dict, FACTORY_CLASS=BreedFactory)
        self.new_data = factory.build(dict, FACTORY_CLASS=BreedFactory)

    def create_breed_obj(self):
        return BreedFactory.create(**self.data)

    # Test cases for adding a new breed object
    # Test Case: #TBV-001
    def test_add_breed_obj_with_valid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#TBV-001: Add breed object with valid token failed"
        )

    # Test Case: #TBV-002
    def test_add_breed_obj_with_expired_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-002: Add breed object with expired token failed"
        )

    # Test Case: #TBV-003
    def test_add_breed_obj_with_invalid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-003: Able to add breed object with invalid token"
        )

    # Test Case: #TBV-004
    def test_add_breed_obj_without_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-004: Able to add breed object without token"
        )

    # test cases for removing an existing breed object
    # Test Case: #TBV-005
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
            "#TBV-005: Remove breed object with valid token failed"
        )

    # Test Case: #TBV-006
    def test_remove_breed_obj_with_expired_token(self):
        breed_obj = self.create_breed_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-006: Able to remove breed object with invalid token"
        )

    # Test Case: #TBV-007
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
            "#TBV-007: Able to remove breed object with invalid token"
        )

    # Test Case: #TBV-008
    def test_remove_breed_obj_without_token(self):
        breed_obj = self.create_breed_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-008: Able to remove breed object without token"
        )

    # test cases for modifying (put) an existing breed object
    # Test Case: #TBV-009
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
            "#TBV-009: Modify breed object with valid token failed"
        )
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'origin': json_data.get('origin', None),
            'description': json_data.get('description', None),
        }
        self.assertEqual(
            modified_data, self.new_data,
            "#TBV-009: Breed object was not modified with valid token"
        )

    # Test Case: #TBV-010
    def test_modify_breed_obj_with_expired_token(self):
        breed_obj = self.create_breed_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=breed_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-010: Able to modify breed object with invalid token"
        )

    # Test Case: #TBV-011
    def test_modify_breed_obj_with_invalid_token(self):
        breed_obj = self.create_breed_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=breed_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-011: Able to modify breed object with invalid token"
        )

    # Test Case: #TBV-012
    def test_modify_breed_obj_without_token(self):
        breed_obj = self.create_breed_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=breed_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-012: Able to modify breed object without token"
        )

    # test cases for partially modifying (patch request) an
    # existing breed object
    # Test Case: #TBV-013
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
            "#TBV-013: partial_modify breed object with valid token failed"
        )
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'origin': json_data.get('origin', None),
            'description': json_data.get('description', None),
        }
        self.assertEqual(
            modified_data, self.data,
            "#TBV-013: Breed object was not partially modified with valid token"
        )

    # Test Case: #TBV-014
    def test_partial_modify_breed_obj_with_expired_token(self):
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
            "#TBV-014: Able to partial_modify breed object with invalid token"
        )

    # Test Case: #TBV-015
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
            "#TBV-015: Able to partial_modify breed object with invalid token"
        )

    # Test Case: #TBV-016
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
            "#TBV-016: Able to partial_modify breed object without token"
        )

    # test cases for retrieving an existing breed object
    # Test Case: #TBV-017
    def test_retrieve_breed_obj_with_valid_token(self):
        breed_obj = self.create_breed_obj()
        response = self.retrieve_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TBV-017: Retrieve one breed object failed"
        )
        json_data = response.json()
        retrieved_data = {
            'name': json_data.get('name', None),
            'origin': json_data.get('origin', None),
            'description': json_data.get('description', None),
        }
        self.assertEqual(
            retrieved_data, self.data,
            "#TBV-017: Retrieve data is not same as the posted data"
        )
