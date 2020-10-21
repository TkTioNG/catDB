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

    def retrieve_obj(self, url, pk, data=None, token=None):
        if token:
            self.login_with_token(token)
        response = self.client.get(reverse(url, args=[pk]), data=data)
        return response

    class Meta:
        abstract = True


class HomeViewSetBaseTests(BaseTestCase):
    '''
    Test Case Code Format: #THV-X00

    Where
    =====            
        X:  A - Add (POST)
            M - Modify (PUT)
            P - Partial Modify (PATCH)
            D - Delete (DELETE)
            R - Retrieve (GET)
    '''

    # initialise before each test case
    def setUp(self):
        self.list_url = 'breeds:home-list'
        self.detail_url = 'breeds:home-detail'
        self.data = factory.build(dict, FACTORY_CLASS=HomeFactory)
        # used as modified data scheme
        self.new_data = factory.build(dict, FACTORY_CLASS=HomeFactory)

    def create_home_obj(self):
        return HomeFactory.create(**self.data)


class HomeViewSetAddTests(HomeViewSetBaseTests):
    '''
    Test Case Code Format: #THV-A00

    Test cases for adding a new home object
    '''

    # Test Case: #THV-A01
    def test_add_home_obj_with_valid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#THV-A01: Add home object with valid token failed"
        )

    # Test Case: #THV-A02
    def test_add_home_obj_with_expired_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-A02: Able to add home object with expired token"
        )

    # Test Case: #THV-A03
    def test_add_home_obj_with_invalid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-A03: Able to add home object with invalid token"
        )

    # Test Case: #THV-A04
    def test_add_home_obj_without_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-A04: Able to add home object without token"
        )


class HomeViewSetDeleteTests(HomeViewSetBaseTests):
    '''
    Test Case Code Format: #THV-D00

    Test cases for deleting an existing home object
    '''

    # Test Case: #THV-D01
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
            "#THV-D01: Remove home object with valid token failed"
        )

    # Test Case: #THV-D02
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
            "#THV-D02: Able to remove home object with expired token"
        )

    # Test Case: #THV-D03
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
            "#THV-D03: Able to remove home object with invalid token"
        )

    # Test Case: #THV-D04
    def test_remove_home_obj_without_token(self):
        home_obj = self.create_home_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-D04: Able to remove home object without token"
        )


class HomeViewSetModifyTests(HomeViewSetBaseTests):
    '''
    Test Case Code Format: #THV-M00

    Test cases for modifying (put) an existing home object
    '''

    # Test Case: #THV-M01
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
            "#THV-M01: Modify home object with valid token failed"
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
            "#THV-M01: Home object was not modified with valid token"
        )

    # Test Case: #THV-M02
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
            "#THV-M02: Able to modify home object with expired token"
        )

    # Test Case: #THV-M03
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
            "#THV-M03: Able to modify home object with invalid token"
        )

    # Test Case: #THV-M04
    def test_modify_home_obj_without_token(self):
        home_obj = self.create_home_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=home_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-M04: Able to modify home object without token"
        )


class HomeViewSetPartialModifyTests(HomeViewSetBaseTests):
    '''
    Test Case Code Format: #THV-P00

    Test cases for partially modifying (patch request) an
    existing home object
    '''

    # Test Case: #THV-P01
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
            "#THV-P01: partial_modify Home object with valid token failed"
        )
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'address': json_data.get('address', None),
            'hometype': json_data.get('hometype', None),
        }
        self.assertEqual(
            modified_data, self.data,
            "#THV-P01: Home object was not partially modified with valid token"
        )

    # Test Case: #THV-P02
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
            "#THV-P02: Able to partial_modify home object with expired token"
        )

    # Test Case: #THV-P03
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
            "#THV-P03: Able to partial_modify home object with invalid token"
        )

    # Test Case: #THV-P04
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
            "#THV-P04: Able to partial_modify home object without token"
        )


class HomeViewSetRetrieveTests(HomeViewSetBaseTests):
    '''
    Test Case Code Format: #THV-R00

    Test cases for retrieving an existing home object
    '''

    # Test Case: #THV-R01
    def test_retrieve_home_obj_with_valid_token(self):
        home_obj = self.create_home_obj()
        response = self.retrieve_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#THV-R01: Retrieve one home object failed"
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
            "#THV-R01: Retrieve data is not same as the posted data"
        )


class BreedViewSetBaseTests(BaseTestCase):
    '''
    Test Case Code Format: #TBV-X00

    Where
    =====            
        X:  A - Add (POST)
            M - Modify (PUT)
            P - Partial Modify (PATCH)
            D - Delete (DELETE)
            R - Retrieve (GET)
    '''

    # initialise before each test case
    def setUp(self):
        self.list_url = 'breeds:breed-list'
        self.detail_url = 'breeds:breed-detail'
        self.data = factory.build(dict, FACTORY_CLASS=BreedFactory)
        # dict of Breed object as modifying data scheme
        self.new_data = factory.build(dict, FACTORY_CLASS=BreedFactory)

    def create_breed_obj(self):
        return BreedFactory.create(**self.data)


class BreedViewSetAddTests(BreedViewSetBaseTests):
    '''
    Test Case Code Format: #TBV-A00

    Test cases for adding a new breed object
    '''
    # Test Case: #TBV-A01

    def test_add_breed_obj_with_valid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#TBV-A01: Add breed object with valid token failed"
        )

    # Test Case: #TBV-A02
    def test_add_breed_obj_with_expired_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-A02: Add breed object with expired token failed"
        )

    # Test Case: #TBV-A03
    def test_add_breed_obj_with_invalid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-A03: Able to add breed object with invalid token"
        )

    # Test Case: #TBV-A04
    def test_add_breed_obj_without_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-A04: Able to add breed object without token"
        )


class BreedViewSetDeleteTests(BreedViewSetBaseTests):
    '''
    Test Case Code Format: #TBV-D00

    Test cases for removing an existing breed object
    '''

    # Test Case: #TBV-D01
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
            "#TBV-D01: Remove breed object with valid token failed"
        )

    # Test Case: #TBV-D02
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
            "#TBV-D02: Able to remove breed object with invalid token"
        )

    # Test Case: #TBV-D03
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
            "#TBV-D03: Able to remove breed object with invalid token"
        )

    # Test Case: #TBV-D04
    def test_remove_breed_obj_without_token(self):
        breed_obj = self.create_breed_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-D04: Able to remove breed object without token"
        )


class BreedViewSetModifyTests(BreedViewSetBaseTests):
    '''
    Test Case Code Format: #TBV-M00

    Test cases for modifying (put) an existing breed object
    '''

    # Test Case: #TBV-M01
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
            "#TBV-M01: Modify breed object with valid token failed"
        )
        json_data = response.json()
        modified_data = {
            'name': json_data.get('name', None),
            'origin': json_data.get('origin', None),
            'description': json_data.get('description', None),
        }
        self.assertEqual(
            modified_data, self.new_data,
            "#TBV-M01: Breed object was not modified with valid token"
        )

    # Test Case: #TBV-M02
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
            "#TBV-M02: Able to modify breed object with invalid token"
        )

    # Test Case: #TBV-M03
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
            "#TBV-M03: Able to modify breed object with invalid token"
        )

    # Test Case: #TBV-M04
    def test_modify_breed_obj_without_token(self):
        breed_obj = self.create_breed_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=breed_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-M04: Able to modify breed object without token"
        )


class BreedViewSetPartialModifyTests(BreedViewSetBaseTests):
    '''
    Test Case Code Format: #TBV-P00

    Test cases for partially modifying (patch request) an
    existing breed object
    '''

    # Test Case: #TBV-P01
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
            "#TBV-P01: partial_modify breed object with valid token failed"
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
            "#TBV-P01: Breed object was not partially modified with valid token"
        )

    # Test Case: #TBV-P02
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
            "#TBV-P02: Able to partial_modify breed object with invalid token"
        )

    # Test Case: #TBV-P03
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
            "#TBV-P03: Able to partial_modify breed object with invalid token"
        )

    # Test Case: #TBV-P04
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
            "#TBV-P04: Able to partial_modify breed object without token"
        )


class BreedViewSetRetrieveTests(BreedViewSetBaseTests):
    '''
    Test Case Code Format: #TBV-R00

    Test cases for retrieving an existing breed object
    '''

    # Test Case: #TBV-R01
    def test_retrieve_breed_obj_with_valid_token(self):
        breed_obj = self.create_breed_obj()
        response = self.retrieve_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TBV-R01: Retrieve one breed object failed"
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
            "#TBV-R01: Retrieve data is not same as the posted data"
        )


class HumanViewSetBaseTests(BaseTestCase):
    '''
    Test Case Code Format: #TPV-X00

    Where
    =====            
        X:  A - Add (POST)
            M - Modify (PUT)
            P - Partial Modify (PATCH)
            D - Delete (DELETE)
            R - Retrieve (GET)
    '''

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


class HumanViewSetAddTests(HumanViewSetBaseTests):
    '''
    Test Case Code Format: #TPV-A00

    Test cases for adding a new human object
    '''

    # Test Case: #TPV-A01
    def test_add_human_obj_with_valid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#TPV-A01: Add human object with valid token failed"
        )

    # Test Case: #TPV-A02
    def test_add_human_obj_with_expired_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-A02: Able to add human object with expired token"
        )

    # Test Case: #TPV-A03
    def test_add_human_obj_with_invalid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-A03: Able to add human object with invalid token"
        )

    # Test Case: #TPV-A04
    def test_add_human_obj_without_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-A04: Able to add human object without token"
        )


class HumanViewSetDeleteTests(HumanViewSetBaseTests):
    '''
    Test Case Code Format: #TPV-D00

    Test cases for removing an existing human object
    '''

    # Test Case: #TPV-D01
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
            "#TPV-D01: Remove human object with valid token failed"
        )

    # Test Case: #TPV-D02
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
            "#TPV-D02: Able to remove human object with expired token"
        )

    # Test Case: #TPV-D03
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
            "#TPV-D03: Able to remove human object with invalid token"
        )

    # Test Case: #TPV-D04
    def test_remove_human_obj_without_token(self):
        human_obj = self.create_human_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=human_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-D04: Able to remove human object without token"
        )


class HumanViewSetModifyTests(HumanViewSetBaseTests):
    '''
    Test Case Code Format: #TPV-M00

    Test cases for modifying (put) an existing human object
    '''

    # Test Case: #TPV-M01
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
            "#TPV-M01: Modify human object with valid token failed"
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
            "#TPV-M01: Human object was not modified with valid token"
        )

    # Test Case: #TPV-M02
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
            "#TPV-M02: Able to modify human object with expired token"
        )

    # Test Case: #TPV-M03
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
            "#TPV-M03: Able to modify human object with invalid token"
        )

    # Test Case: #TPV-M04
    def test_modify_human_obj_without_token(self):
        human_obj = self.create_human_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=human_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-M04: Able to modify human object without token"
        )


class HumanViewSetPartialModifyTests(HumanViewSetBaseTests):
    '''
    Test Case Code Format: #TPV-P00

    Test cases for partially modifying (patch request) an
    existing human object
    '''

    # Test Case: #TPV-P01
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
            "#TPV-P01: partial_modify Human object with valid token failed"
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
            "#TPV-P01: Human object was not partially modified with valid token"
        )

    # Test Case: #TPV-P02
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
            "#TPV-P02: Able to partial_modify human object with expired token"
        )

    # Test Case: #TPV-P03
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
            "#TPV-P03: Able to partial_modify human object with invalid token"
        )

    # Test Case: #TPV-P04
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
            "#TPV-P04: Able to partial_modify human object without token"
        )


class HumanViewSetRetrieveTests(HumanViewSetBaseTests):
    '''
    Test Case Code Format: #TPV-R00

    Test cases for retrieving an existing human object
    '''

    # Test Case: #TPV-R01
    def test_retrieve_human_obj_with_valid_token(self):
        human_obj = self.create_human_obj()
        response = self.retrieve_obj(
            url=self.detail_url,
            pk=human_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TPV-R01: Retrieve one human object failed"
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
            "#TPV-R01: Retrieve data is not same as the posted data"
        )


class CatViewSetBaseTests(BaseTestCase):
    '''
    Test Case Code Format: #TCV-X00

    Where
    =====            
        X:  A - Add (POST)
            M - Modify (PUT)
            P - Partial Modify (PATCH)
            D - Delete (DELETE)
            R - Retrieve (GET)
    '''

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


class CatViewSetAddTests(CatViewSetBaseTests):
    '''
    Test Case Code Format: #TCV-A00

    Test cases for adding a new cat object
    '''

    # Test Case: #TCV-A01
    def test_add_cat_obj_with_valid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#TCV-A01: Add cat object with valid token failed"
        )

    # Test Case: #TCV-A02
    def test_add_cat_obj_with_expired_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-A02: Able to add cat object with expired token"
        )

    # Test Case: #TCV-A03
    def test_add_cat_obj_with_invalid_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-A03: Able to add cat object with invalid token"
        )

    # Test Case: #TCV-A04
    def test_add_cat_obj_without_token(self):
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-A04: Able to add cat object without token"
        )


class CatViewSetDeleteTests(CatViewSetBaseTests):
    '''
    Test Case Code Format: #TCV-D00

    Test cases for removing an existing cat object
    '''

    # Test Case: #TCV-D01
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
            "#TCV-D01: Remove cat object with valid token failed"
        )

    # Test Case: #TCV-D02
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
            "#TCV-D02: Able to remove cat object with expired token"
        )

    # Test Case: #TCV-D03
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
            "#TCV-D03: Able to remove cat object with invalid token"
        )

    # Test Case: #TCV-D04
    def test_remove_cat_obj_without_token(self):
        cat_obj = self.create_cat_obj()
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=cat_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-D04: Able to remove cat object without token"
        )


class CatViewSetModifyTests(CatViewSetBaseTests):
    '''
    Test Case Code Format: #TCV-M00

    Test cases for modifying (put) an existing cat object
    '''

    # Test Case: #TCV-M01
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
            "#TCV-M01: Modify cat object with valid token failed"
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
            "#TCV-M01: Cat object was not modified with valid token"
        )

    # Test Case: #TCV-M02
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
            "#TCV-M02: Able to modify cat object with expired token"
        )

    # Test Case: #TCV-M03
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
            "#TCV-M03: Able to modify cat object with invalid token"
        )

    # Test Case: #TCV-M04
    def test_modify_cat_obj_without_token(self):
        cat_obj = self.create_cat_obj()
        response = self.modify_obj(
            url=self.detail_url,
            data=self.new_data,
            pk=cat_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-M04: Able to modify cat object without token"
        )


class CatViewSetPartialModifyTests(CatViewSetBaseTests):
    '''
    Test Case Code Format: #TCV-P00

    Test cases for partially modifying (patch request) an
    existing cat object
    '''

    # Test Case: #TCV-P01
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
            "#TCV-P01: partial_modify Cat object with valid token failed"
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
            "#TCV-P01: Cat object was not partially modified with valid token"
        )

    # Test Case: #TCV-P02
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
            "#TCV-P02: Able to partial_modify cat object with expired token"
        )

    # Test Case: #TCV-P03
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
            "#TCV-P03: Able to partial_modify cat object with invalid token"
        )

    # Test Case: #TCV-P04
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
            "#TCV-P04: Able to partial_modify cat object without token"
        )


class CatViewSetRetrieveTests(CatViewSetBaseTests):
    '''
    Test Case Code Format: #TCV-R00

    Test cases for retrieving an existing cat object
    '''

    # Test Case: #TCV-R01
    def test_retrieve_cat_obj_with_valid_token(self):
        cat_obj = self.create_cat_obj()
        response = self.retrieve_obj(
            url=self.detail_url,
            pk=cat_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TCV-R01: Retrieve one cat object failed"
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
            "#TCV-R01: Retrieve data is not same as the posted data"
        )
