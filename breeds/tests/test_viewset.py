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

from breeds.factories import BreedFactory, CatFactory, HomeFactory, HumanFactory
from breeds.authentication import EXPIRING_HOUR

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

# TODO: Add negative test case
class BaseTestCase(APITestCase):
    '''
    Base Test Case Template that provide `add (POST)`, `remove (DELETE)`, 
    `modify (PUT)`, `partial modify (PATCH)`, `retrieve (GET)` function.
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

    def retrieve_obj(self, url, pk, data=None, token=None):
        if token:
            self.login_with_token(token)
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
        # used as modified data scheme
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
        # attempt to remove the home_obj created
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
        # Convert http response to json for comparing purpose
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
        self.data['name'] = "modify test name"  # modifying name only
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
        # Convert http response to json for comparing purpose
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
        # dict of Breed object as modifying data scheme
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
        # Convert http response to json for comparing purpose
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
        # Convert http response to json for comparing purpose
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


class HumanViewSetTests(BaseTestCase):
    # Test Case Code Format; #TPV-000
    # Current Test Case Sequence: TPV-017

    # initialise before each test case
    def setUp(self):
        self.list_url = 'breeds:human-list'
        self.detail_url = 'breeds:human-detail'

        # home FK is created before creating the Human object
        self.data = factory.build(
            dict, FACTORY_CLASS=HumanFactory, home=HomeFactory.create())
        # Serve as the modifying data scheme
        self.new_data = factory.build(
            dict, FACTORY_CLASS=HumanFactory, home=HomeFactory.create())
        # Parsing the human object into acceptable dict object
        self.parse_obj(self.data, self.new_data)

    def parse_obj(self, *dicts):
        for d in dicts:
            # convert FK to hyperlink
            d['home'] = 'http://testserver' \
                        + reverse('breeds:home-detail', args=[d['home'].id])
            # convert datetime object into str, default format(yyyy-mm-dd)
            d['date_of_birth'] = str(d['date_of_birth'])

    def create_human_obj(self):
        return HumanFactory.create()

    # Test cases for adding a new human object
    # Test Case: #TPV-001
    def test_add_human_obj_with_valid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#TPV-001: Add human object with valid token failed"
        )

    # Test Case: #TPV-002
    def test_add_human_obj_with_expired_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-002: Able to add human object with expired token"
        )

    # Test Case: #TPV-003
    def test_add_human_obj_with_invalid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-003: Able to add human object with invalid token"
        )

    # Test Case: #TPV-004
    def test_add_human_obj_without_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-004: Able to add human object without token"
        )

    # test cases for removing an existing human object
    # Test Case: #TPV-005
    def test_remove_human_obj_with_valid_token(self):
        human_obj = self.create_human_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=human_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "#TPV-005: Remove human object with valid token failed"
        )

    # Test Case: #TPV-006
    def test_remove_human_obj_with_expired_token(self):
        human_obj = self.create_human_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=human_obj.pk,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-006: Able to remove human object with expired token"
        )

    # Test Case: #TPV-007
    def test_remove_human_obj_with_invalid_token(self):
        human_obj = self.create_human_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=human_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-007: Able to remove human object with invalid token"
        )

    # Test Case: #TPV-008
    def test_remove_human_obj_without_token(self):
        human_obj = self.create_human_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=human_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-008: Able to remove human object without token"
        )

    # test cases for modifying (put) an existing human object
    # Test Case: #TPV-009
    def test_modify_human_obj_with_valid_token(self):
        human_obj = self.create_human_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=human_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TPV-009: Modify human object with valid token failed"
        )
        # convert http response into json for comparing purpose
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'gender': json_data.get('gender', None),
            'date_of_birth': json_data.get('date_of_birth', None),
            'description': json_data.get('description', None),
            'home': json_data.get('home', None),
        }
        self.assertEqual(
            modified_data, self.new_data,
            "#TPV-009: Human object was not modified with valid token"
        )

    # Test Case: #TPV-010
    def test_modify_human_obj_with_expired_token(self):
        human_obj = self.create_human_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=human_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-010: Able to modify human object with expired token"
        )

    # Test Case: #TPV-011
    def test_modify_human_obj_with_invalid_token(self):
        human_obj = self.create_human_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=human_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-011: Able to modify human object with invalid token"
        )

    # Test Case: #TPV-012
    def test_modify_human_obj_without_token(self):
        human_obj = self.create_human_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=human_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-012: Able to modify human object without token"
        )

    # test cases for partially modifying (patch request) an
    # existing human object
    # Test Case: #TPV-013
    def test_partial_modify_human_obj_with_valid_token(self):
        human_obj = self.create_human_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=human_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TPV-013: partial_modify Human object with valid token failed"
        )
        # convert http response into json for comparing purpose
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'gender': json_data.get('gender', None),
            'date_of_birth': json_data.get('date_of_birth', None),
            'description': json_data.get('description', None),
            'home': json_data.get('home', None),
        }
        self.assertEqual(
            modified_data, self.data,
            "#TPV-013: Human object was not partially modified with valid token"
        )

    # Test Case: #TPV-014
    def test_partial_modify_human_obj_with_expired_token(self):
        human_obj = self.create_human_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=human_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-014: Able to partial_modify human object with expired token"
        )

    # Test Case: #TPV-015
    def test_partial_modify_human_obj_with_invalid_token(self):
        human_obj = self.create_human_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=human_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-015: Able to partial_modify human object with invalid token"
        )

    # Test Case: #TPV-016
    def test_partial_modify_human_obj_without_token(self):
        human_obj = self.create_human_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=human_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-016: Able to partial_modify human object without token"
        )

    # test cases for retrieving an existing human object
    # Test Case: #TPV-017
    def test_retrieve_human_obj_with_valid_token(self):
        human_obj = self.create_human_obj()
        response = self.retrieve_obj(
            url=self.detail_url,
            pk=human_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TPV-017: Retrieve one human object failed"
        )
        # convert http response into json for comparing purpose
        json_data = response.json()
        retrieved_data = {
            'name': json_data.get('name', None),
            'gender': json_data.get('gender', None),
            'date_of_birth': json_data.get('date_of_birth', None),
            'description': json_data.get('description', None),
            'home': json_data.get('home', None),
        }
        # convert the human object created above into dict
        # to compare with the http response above
        human_obj = {
            'name': human_obj.name,
            'gender': human_obj.gender,
            'date_of_birth': human_obj.date_of_birth,
            'description': human_obj.description,
            'home': human_obj.home,
        }
        # parse the dict object into the same standards as from the API
        self.parse_obj(human_obj)
        self.assertEqual(
            retrieved_data, human_obj,
            "#TPV-017: Retrieve data is not same as the posted data"
        )


class CatViewSetTests(BaseTestCase):
    # Test Case Code Format; #TCV-000
    # Current Test Case Sequence: TCV-017

    # initialise before each test case
    def setUp(self):
        self.list_url = 'breeds:cat-list'
        self.detail_url = 'breeds:cat-detail'

        # Breed and Human FKs are created before creating the Cat object
        self.data = factory.build(dict, FACTORY_CLASS=CatFactory,
                                  breed=BreedFactory.create(),
                                  owner=HumanFactory.create())
        # Serve as the modifying data scheme
        self.new_data = factory.build(dict, FACTORY_CLASS=CatFactory,
                                      breed=BreedFactory.create(),
                                      owner=HumanFactory.create())
        # Parsing the cat object into acceptable dict object
        self.parse_obj(self.data, self.new_data)

    def parse_obj(self, *dicts):
        for d in dicts:
            # convert FKs to hyperlinks
            d['breed'] = 'http://testserver' \
                        + reverse('breeds:breed-detail', args=[d['breed'].id])
            d['owner'] = 'http://testserver' \
                        + reverse('breeds:human-detail', args=[d['owner'].id])
            # convert datetime object into str, default format(yyyy-mm-dd)
            d['date_of_birth'] = str(d['date_of_birth'])

    def create_cat_obj(self):
        return CatFactory.create()

    # Test cases for adding a new cat object
    # Test Case: #TCV-001
    def test_add_cat_obj_with_valid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#TCV-001: Add cat object with valid token failed"
        )

    # Test Case: #TCV-002
    def test_add_cat_obj_with_expired_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-002: Able to add cat object with expired token"
        )

    # Test Case: #TCV-003
    def test_add_cat_obj_with_invalid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-003: Able to add cat object with invalid token"
        )

    # Test Case: #TCV-004
    def test_add_cat_obj_without_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-004: Able to add cat object without token"
        )

    # test cases for removing an existing cat object
    # Test Case: #TCV-005
    def test_remove_cat_obj_with_valid_token(self):
        cat_obj = self.create_cat_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=cat_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "#TCV-005: Remove cat object with valid token failed"
        )

    # Test Case: #TCV-006
    def test_remove_cat_obj_with_expired_token(self):
        cat_obj = self.create_cat_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=cat_obj.pk,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-006: Able to remove cat object with expired token"
        )

    # Test Case: #TCV-007
    def test_remove_cat_obj_with_invalid_token(self):
        cat_obj = self.create_cat_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=cat_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-007: Able to remove cat object with invalid token"
        )

    # Test Case: #TCV-008
    def test_remove_cat_obj_without_token(self):
        cat_obj = self.create_cat_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=cat_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-008: Able to remove cat object without token"
        )

    # test cases for modifying (put) an existing cat object
    # Test Case: #TCV-009
    def test_modify_cat_obj_with_valid_token(self):
        cat_obj = self.create_cat_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=cat_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TCV-009: Modify cat object with valid token failed"
        )
        # convert http response into json for comparing purpose
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'gender': json_data.get('gender', None),
            'date_of_birth': json_data.get('date_of_birth', None),
            'description': json_data.get('description', None),
            'breed': json_data.get('breed', None),
            'owner': json_data.get('owner', None),
        }
        self.assertEqual(
            modified_data, self.new_data,
            "#TCV-009: Cat object was not modified with valid token"
        )

    # Test Case: #TCV-010
    def test_modify_cat_obj_with_expired_token(self):
        cat_obj = self.create_cat_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=cat_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-010: Able to modify cat object with expired token"
        )

    # Test Case: #TCV-011
    def test_modify_cat_obj_with_invalid_token(self):
        cat_obj = self.create_cat_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=cat_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-011: Able to modify cat object with invalid token"
        )

    # Test Case: #TCV-012
    def test_modify_cat_obj_without_token(self):
        cat_obj = self.create_cat_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=cat_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-012: Able to modify cat object without token"
        )

    # test cases for partially modifying (patch request) an
    # existing cat object
    # Test Case: #TCV-013
    def test_partial_modify_cat_obj_with_valid_token(self):
        cat_obj = self.create_cat_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=cat_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TCV-013: partial_modify Cat object with valid token failed"
        )
        # convert http response into json for comparing purpose
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'gender': json_data.get('gender', None),
            'date_of_birth': json_data.get('date_of_birth', None),
            'description': json_data.get('description', None),
            'breed': json_data.get('breed', None),
            'owner': json_data.get('owner', None),
        }
        self.assertEqual(
            modified_data, self.data,
            "#TCV-013: Cat object was not partially modified with valid token"
        )

    # Test Case: #TCV-014
    def test_partial_modify_cat_obj_with_expired_token(self):
        cat_obj = self.create_cat_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=cat_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-014: Able to partial_modify cat object with expired token"
        )

    # Test Case: #TCV-015
    def test_partial_modify_cat_obj_with_invalid_token(self):
        cat_obj = self.create_cat_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=cat_obj.pk,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-015: Able to partial_modify cat object with invalid token"
        )

    # Test Case: #TCV-016
    def test_partial_modify_cat_obj_without_token(self):
        cat_obj = self.create_cat_obj()
        self.data['name'] = "modify test name"
        response = self.partial_modify_obj(
            url=self.detail_url,
            data=self.data,
            pk=cat_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-016: Able to partial_modify cat object without token"
        )

    # test cases for retrieving an existing cat object
    # Test Case: #TCV-017
    def test_retrieve_cat_obj_with_valid_token(self):
        cat_obj = self.create_cat_obj()
        response = self.retrieve_obj(
            url=self.detail_url,
            pk=cat_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TCV-017: Retrieve one cat object failed"
        )
        # convert http response into json for comparing purpose
        json_data = response.json()
        retrieved_data = {
            'name': json_data.get('name', None),
            'gender': json_data.get('gender', None),
            'date_of_birth': json_data.get('date_of_birth', None),
            'description': json_data.get('description', None),
            'breed': json_data.get('breed', None),
            'owner': json_data.get('owner', None),
        }
        # convert the cat object created above into dict
        # to compare with the http response above
        cat_obj = {
            'name': cat_obj.name,
            'gender': cat_obj.gender,
            'date_of_birth': cat_obj.date_of_birth,
            'description': cat_obj.description,
            'breed': cat_obj.breed,
            'owner': cat_obj.owner,
        }
        # parse the dict object into the same standards as from the API
        self.parse_obj(cat_obj)
        self.assertEqual(
            retrieved_data, cat_obj,
            "#TCV-017: Retrieve data is not same as the posted data"
        )
