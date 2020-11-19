import string
import random
import factory
import requests
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token

from catapp.models import Breed, Cat, Home, Human
from catapp.factories import BreedFactory, CatFactory, HomeFactory, HumanFactory
from catapp.tests.base import convert_id_to_hyperlink, ViewName as vn


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
        self.list_url = vn.HOME_VIEW_LIST
        self.detail_url = vn.HOME_VIEW_DETAIL
        self.data = factory.build(dict, FACTORY_CLASS=HomeFactory)
        # used as modified data scheme
        self.new_data = factory.build(dict, FACTORY_CLASS=HomeFactory)

    def create_home_obj(self):
        return HomeFactory.create(**self.data)

    def get_home_obj_url(self, data: dict):
        # Add url (hyperlink) from the home object id to the dict object
        home_obj = Home.objects.latest('pk')
        data['url'] = convert_id_to_hyperlink(vn.HOME_VIEW_DETAIL, home_obj)
        return data


class HomeViewSetAddTests(HomeViewSetBaseTests):
    '''
    Test Case Code Format: #THV-A00

    Test cases for adding a new home object
    '''

    # Test Case: #THV-A01
    def test_add_home_obj_with_valid_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#THV-A01: Add home object with valid token failed"
        )
        self.assertEqual(
            response.json(), self.get_home_obj_url(self.data),
            "#THV-A01: Add objects is not the same"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj + 1,
            "#THV-A01: Home object is not added in the total count"
        )

    # Test Case: #THV-A02
    def test_add_home_obj_with_expired_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-A02: Able to add home object with expired token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#THV-A02: Home object is accidentally added to total count"
        )

    # Test Case: #THV-A03
    def test_add_home_obj_with_invalid_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-A03: Able to add home object with invalid token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#THV-A03: Home object is accidentally added to total count"
        )

    # Test Case: #THV-A04
    def test_add_home_obj_without_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-A04: Able to add home object without token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#THV-A04: Home object is accidentally added to total count"
        )

    # Test Case: #THV-A05
    def test_add_home_obj_in_wrong_url(self):
        num_of_home_obj = self.get_num_of_obj(self.list_url)
        num_of_breed_obj = self.get_num_of_obj(vn.BREED_VIEW_LIST)
        # Attempt to add home obj in breed endpoint
        response = self.add_obj(
            url=vn.BREED_VIEW_LIST,
            data=self.data,
            token=get_valid_token_key()
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#THV-A05: Bad Request was not produced"
        )
        new_num_of_home_obj = self.get_num_of_obj(self.list_url)
        new_num_of_breed_obj = self.get_num_of_obj(vn.BREED_VIEW_LIST)
        self.assertEqual(
            new_num_of_home_obj, num_of_home_obj,
            "#THV-A05: Home object is accidentally added to total count"
        )
        self.assertEqual(
            new_num_of_home_obj, num_of_home_obj,
            "#THV-A05: Home object is accidentally added to home total count"
        )

    # Test Case: #THV-A06
    def test_add_home_obj_with_invalid_data(self):
        num_of_home_obj = self.get_num_of_obj(self.list_url)

        # Generate Breed data as invalid data for Home instance
        invalid_data = factory.build(dict, FACTORY_CLASS=BreedFactory)
        response = self.add_obj(
            url=self.list_url,
            data=invalid_data,
            token=get_valid_token_key()
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#THV-A06: Able to add home object with invalid data"
        )
        new_num_of_home_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_home_obj, num_of_home_obj,
            "#THV-A06: Home object is accidentally added to total count"
        )


class HomeViewSetDeleteTests(HomeViewSetBaseTests):
    '''
    Test Case Code Format: #THV-D00

    Test cases for deleting an existing home object
    '''

    # Test Case: #THV-D01
    def test_remove_home_obj_with_valid_token(self):
        home_obj = self.create_home_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
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
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj - 1,
            "#THV-D01: Total no. of objects is not reduced by 1"
        )

    # Test Case: #THV-D02

    def test_remove_home_obj_with_expired_token(self):
        home_obj = self.create_home_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
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
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#THV-D02: Total no. of objects is unexpectedly reduced"
        )

    # Test Case: #THV-D03
    def test_remove_home_obj_with_invalid_token(self):
        home_obj = self.create_home_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
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
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#THV-D03: Total no. of objects is unexpectedly reduced"
        )

    # Test Case: #THV-D04
    def test_remove_home_obj_without_token(self):
        home_obj = self.create_home_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=home_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#THV-D04: Able to remove home object without token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#THV-D04: Total no. of objects is unexpectedly reduced"
        )

    # Test Case: #THV-D05
    def test_remove_not_existing_home_obj(self):
        HomeFactory.create_batch(10)
        num_of_obj = self.get_num_of_obj(self.list_url)

        response = self.remove_obj(
            url=self.detail_url,
            data=None,
            pk=99,
            token=get_valid_token_key()
        )
        self.assertNotEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "#THV-D05: Delete operation accidentally succeed"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND,
            "#THV-D05: Non-existing page was somehow reached"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#THV-D05: Total no. of objects is unexpectedly reduced"
        )

    # Test Case: #THV-D06
    def test_remove_home_obj_in_wrong_url(self):
        home_obj = self.create_home_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
        num_of_cat_obj = self.get_num_of_obj(vn.CAT_VIEW_LIST)

        # Attempt to delete home instance in cat endpoint
        response = self.remove_obj(
            url=vn.CAT_VIEW_DETAIL,
            data=self.data,
            pk=home_obj.pk,
            token=get_valid_token_key()
        )
        self.assertNotEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "#THV-D06: Delete operation accidentally succeed"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND,
            "#THV-D06: Non-existing page was somehow reached"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#THV-D06: Total no. of objects is unexpectedly reduced"
        )
        new_num_of_cat_obj = self.get_num_of_obj(vn.CAT_VIEW_LIST)
        self.assertEqual(
            new_num_of_cat_obj, num_of_cat_obj,
            "#THV-D06: Total no. of objects is unexpectedly reduced"
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
        self.assertEqual(
            response.json(), self.get_home_obj_url(self.new_data),
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

    # Test Case: #THV-M05
    def test_modify_home_obj_with_invalid_data(self):
        home_obj = self.create_home_obj()

        # Generate Breed data as invalid data for Home instance
        invalid_data = factory.build(dict, FACTORY_CLASS=BreedFactory)
        response = self.modify_obj(
            url=self.detail_url,
            data=invalid_data,
            pk=home_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#THV-M05: Able to modify home object with invalid data"
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
        self.assertEqual(
            response.json(), self.get_home_obj_url(self.data),
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
    def test_retrieve_home_obj(self):
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
        self.assertEqual(
            response.json(), self.get_home_obj_url(self.data),
            "#THV-R01: Retrieve data is not same as the posted data"
        )

    # Test Case: #THV-R02
    def test_retrieve_multiple_home_obj(self):
        home_objs = HomeFactory.create_batch(10)
        response = self.retrieve_obj(
            url=self.list_url
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#THV-R02: Retrieve home objects failed"
        )
        json_data = response.json()
        self.assertEqual(
            json_data['count'], 10,
            "#THV-R02: Total count of home object is not correct"
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
        self.list_url = vn.BREED_VIEW_LIST
        self.detail_url = vn.BREED_VIEW_DETAIL
        self.data = factory.build(dict, FACTORY_CLASS=BreedFactory)
        # dict of Breed object as modifying data scheme
        self.new_data = factory.build(dict, FACTORY_CLASS=BreedFactory)

    def create_breed_obj(self):
        return BreedFactory.create(**self.data)

    def get_breed_obj_url(self, data: dict):
        # Add url (hyperlink) from the breed object id to the dict object
        breed_obj = Breed.objects.latest('pk')
        data['url'] = convert_id_to_hyperlink(vn.BREED_VIEW_DETAIL, breed_obj)

        try:
            data['cats'] = []
            data['homes'] = []
            cats = Cat.objects.filter(breed=breed_obj)
            for cat in cats:
                data['cats'].append(
                    convert_id_to_hyperlink(vn.CAT_VIEW_DETAIL, cat)
                )
                data['homes'].append(
                    convert_id_to_hyperlink(
                        vn.HOME_VIEW_DETAIL, cat.owner.home)
                )
        except Cat.DoesNotExist:
            data['cats'] = []
            data['homes'] = []
        return data


class BreedViewSetAddTests(BreedViewSetBaseTests):
    '''
    Test Case Code Format: #TBV-A00

    Test cases for adding a new breed object
    '''
    # Test Case: #TBV-A01

    def test_add_breed_obj_with_valid_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#TBV-A01: Add breed object with valid token failed"
        )
        self.assertEqual(
            response.json(), self.get_breed_obj_url(self.data),
            "#TBV-A01: Add objects is not the same"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj + 1,
            "#TBV-A01: Breed object is not added in the total count"
        )

    # Test Case: #TBV-A02
    def test_add_breed_obj_with_expired_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-A02: Add breed object with expired token failed"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TBV-A02: Breed object is accidentally added to total count"
        )

    # Test Case: #TBV-A03
    def test_add_breed_obj_with_invalid_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-A03: Able to add breed object with invalid token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TBV-A03: Breed object is accidentally added to total count"
        )

    # Test Case: #TBV-A04
    def test_add_breed_obj_without_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-A04: Able to add breed object without token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TBV-A04: Breed object is accidentally added to total count"
        )

    # Test Case: #TBV-A05
    def test_add_breed_obj_in_wrong_url(self):
        num_of_breed_obj = self.get_num_of_obj(self.list_url)
        num_of_home_obj = self.get_num_of_obj(vn.HOME_VIEW_LIST)
        # Attempt to add breed obj in home endpoint
        response = self.add_obj(
            url=vn.HOME_VIEW_LIST,
            data=self.data,
            token=get_valid_token_key()
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#TBV-A05: Bad Request was not produced"
        )
        new_num_of_breed_obj = self.get_num_of_obj(self.list_url)
        new_num_of_home_obj = self.get_num_of_obj(vn.HOME_VIEW_LIST)
        self.assertEqual(
            new_num_of_breed_obj, num_of_breed_obj,
            "#TBV-A05: Breed object is accidentally added to total count"
        )
        self.assertEqual(
            new_num_of_home_obj, num_of_home_obj,
            "#TBV-A05: Breed object is accidentally added to home total count"
        )

    # Test Case: #TBV-A06
    def test_add_breed_obj_with_invalid_data(self):
        num_of_breed_obj = self.get_num_of_obj(self.list_url)

        # Generate Home data as invalid data for Breed instance
        invalid_data = factory.build(dict, FACTORY_CLASS=HomeFactory)
        response = self.add_obj(
            url=self.list_url,
            data=invalid_data,
            token=get_valid_token_key()
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#TBV-A06: Able to add breed object with invalid data"
        )
        new_num_of_breed_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_breed_obj, num_of_breed_obj,
            "#TBV-A06: Breed object is accidentally added to total count"
        )


class BreedViewSetDeleteTests(BreedViewSetBaseTests):
    '''
    Test Case Code Format: #TBV-D00

    Test cases for removing an existing breed object
    '''

    # Test Case: #TBV-D01
    def test_remove_breed_obj_with_valid_token(self):
        breed_obj = self.create_breed_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
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
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj - 1,
            "#TBV-D01: Total count of Breed object is not reduced"
        )

    # Test Case: #TBV-D02
    def test_remove_breed_obj_with_expired_token(self):
        breed_obj = self.create_breed_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
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
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TBV-D02: Total count of Breed object is unexpectedly reduced"
        )

    # Test Case: #TBV-D03
    def test_remove_breed_obj_with_invalid_token(self):
        breed_obj = self.create_breed_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
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
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TBV-D03: Total count of Breed object is unexpectedly reduced"
        )

    # Test Case: #TBV-D04
    def test_remove_breed_obj_without_token(self):
        breed_obj = self.create_breed_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=breed_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TBV-D04: Able to remove breed object without token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TBV-D04: Total count of Breed object is unexpectedly reduced"
        )

    # Test Case: #TBV-D05
    def test_remove_not_existing_breed_obj(self):
        breed_obj = self.create_breed_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)

        response = self.remove_obj(
            url=self.detail_url,
            data=None,
            pk=99,
            token=get_valid_token_key()
        )
        self.assertNotEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "#TBV-D05: Delete operation accidentally succeed"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND,
            "#TBV-D05: Non-existing page was somehow reached"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TBV-D05: Total no. of objects is unexpectedly reduced"
        )

    # Test Case: #TBV-D06
    def test_remove_breed_obj_in_wrong_url(self):
        breed_obj = self.create_breed_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
        num_of_cat_obj = self.get_num_of_obj(vn.CAT_VIEW_LIST)

        # Attempt to delete breed instance in cat endpoint
        response = self.remove_obj(
            url=vn.CAT_VIEW_DETAIL,
            data=self.data,
            pk=breed_obj.pk,
            token=get_valid_token_key()
        )
        self.assertNotEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "#TBV-D06: Delete operation accidentally succeed"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND,
            "#TBV-D06: Non-existing page was somehow reached"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TBV-D06: Total no. of objects is unexpectedly reduced"
        )
        new_num_of_cat_obj = self.get_num_of_obj(vn.CAT_VIEW_LIST)
        self.assertEqual(
            new_num_of_cat_obj, num_of_cat_obj,
            "#TBV-D06: Total no. of objects is unexpectedly reduced"
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
        self.assertEqual(
            response.json(), self.get_breed_obj_url(self.new_data),
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

    # Test Case: #TBV-M05
    def test_modify_breed_obj_with_invalid_data(self):
        breed_obj = self.create_breed_obj()

        # Generate Home data as invalid data for Breed instance
        invalid_data = factory.build(dict, FACTORY_CLASS=HomeFactory)
        response = self.modify_obj(
            url=self.detail_url,
            data=invalid_data,
            pk=breed_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#TBV-M05: Able tp modify breed object with invalid data"
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
        self.assertEqual(
            response.json(), self.get_breed_obj_url(self.data),
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
        self.assertEqual(
            response.json(), self.get_breed_obj_url(self.data),
            "#TBV-R01: Retrieve data is not same as the posted data"
        )

    # Test Case: #TBV-R02
    def test_retrieve_multiple_breed_obj(self):
        breed_objs = BreedFactory.create_batch(10)
        response = self.retrieve_obj(
            url=self.list_url
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TBV-R02: Retrieve breed objects failed"
        )
        json_data = response.json()
        self.assertEqual(
            json_data['count'], 10,
            "#TBV-R02: Total count of breed object is not correct"
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
        self.list_url = vn.HUMAN_VIEW_LIST
        self.detail_url = vn.HUMAN_VIEW_DETAIL

        # home FK is created before creating the Human object
        self.home = HomeFactory.create()
        self.data = factory.build(
            dict, FACTORY_CLASS=HumanFactory, home=self.home)
        # Serve as the modifying data scheme
        self.new_data = factory.build(
            dict, FACTORY_CLASS=HumanFactory, home=HomeFactory.create())
        # Parsing the human object into acceptable dict object
        self.parse_obj(self.data, self.new_data)

    def parse_obj(self, *dicts):
        for d in dicts:
            # convert FK to hyperlink
            d['home'] = convert_id_to_hyperlink(vn.HOME_VIEW_DETAIL,
                                                d['home'])
            # convert datetime object into str, default format(yyyy-mm-dd)
            d['date_of_birth'] = str(d['date_of_birth'])

    def create_human_obj(self):
        data = self.data.copy()
        data['home'] = self.home
        return HumanFactory.create(**data)

    def get_human_obj_url(self, data: dict):
        # Add url (hyperlink) from the human object id to the dict object
        human_obj = Human.objects.latest('pk')
        data['url'] = convert_id_to_hyperlink(vn.HUMAN_VIEW_DETAIL, human_obj)

        try:
            data['cats'] = []
            cats = Cat.objects.filter(owner=human_obj)
            for cat in cats:
                data['cats'].append(
                    convert_id_to_hyperlink(vn.CAT_VIEW_DETAIL, cat)
                )
        except Cat.DoesNotExist:
            data['cats'] = []
        return data


class HumanViewSetAddTests(HumanViewSetBaseTests):
    '''
    Test Case Code Format: #TPV-A00

    Test cases for adding a new human object
    '''

    # Test Case: #TPV-A01
    def test_add_human_obj_with_valid_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#TPV-A01: Add human object with valid token failed"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj + 1,
            "#TPV-A01: Human object is not added in the total count"
        )

    # Test Case: #TPV-A02
    def test_add_human_obj_with_expired_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-A02: Able to add human object with expired token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TPV-A02: Invalid object is accidentally added to total count"
        )

    # Test Case: #TPV-A03
    def test_add_human_obj_with_invalid_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-A03: Able to add human object with invalid token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TPV-A03: Invalid object is accidentally added to total count"
        )

    # Test Case: #TPV-A04
    def test_add_human_obj_without_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-A04: Able to add human object without token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TPV-A04: Invalid object is accidentally added to total count"
        )

    # Test Case: #TPV-A05
    def test_add_human_obj_in_wrong_url(self):
        num_of_human_obj = self.get_num_of_obj(self.list_url)
        num_of_home_obj = self.get_num_of_obj(vn.HOME_VIEW_LIST)
        # Attempt to add human obj in home endpoint
        response = self.add_obj(
            url=vn.HOME_VIEW_LIST,
            data=self.data,
            token=get_valid_token_key()
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#TPV-A05: Bad Request was not produced"
        )
        new_num_of_human_obj = self.get_num_of_obj(self.list_url)
        new_num_of_home_obj = self.get_num_of_obj(vn.HOME_VIEW_LIST)
        self.assertEqual(
            new_num_of_human_obj, num_of_human_obj,
            "#TPV-A05: Human object is accidentally added to total count"
        )
        self.assertEqual(
            new_num_of_home_obj, num_of_home_obj,
            "#TPV-A05: Human object is accidentally added to home total count"
        )

    # Test Case: #TPV-A06
    def test_add_human_obj_with_invalid_data(self):
        num_of_human_obj = self.get_num_of_obj(self.list_url)

        # Generate Home data as invalid data for Human instance
        invalid_data = factory.build(dict, FACTORY_CLASS=HomeFactory)
        response = self.add_obj(
            url=self.list_url,
            data=invalid_data,
            token=get_valid_token_key()
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#TPV-A06: Able to add human object with invalid data"
        )
        new_num_of_human_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_human_obj, num_of_human_obj,
            "#TPV-A06: Human object is accidentally added to total count"
        )


class HumanViewSetDeleteTests(HumanViewSetBaseTests):
    '''
    Test Case Code Format: #TPV-D00

    Test cases for removing an existing human object
    '''

    # Test Case: #TPV-D01
    def test_remove_human_obj_with_valid_token(self):
        human_obj = self.create_human_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=human_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "#TPV-D01: Remove Human object with valid token failed"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj - 1,
            "#TPV-D01: Total count of Human object is not reduced"
        )

    # Test Case: #TPV-D02
    def test_remove_human_obj_with_expired_token(self):
        human_obj = self.create_human_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
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
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TPV-D02: Total count of Human object is unexpectedly reduced"
        )

    # Test Case: #TPV-D03
    def test_remove_human_obj_with_invalid_token(self):
        human_obj = self.create_human_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
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
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TPV-D03: Total count of Human object is unexpectedly reduced"
        )

    # Test Case: #TPV-D04
    def test_remove_human_obj_without_token(self):
        human_obj = self.create_human_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=human_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TPV-D04: Able to remove human object without token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TPV-D04: Total count of Human object is unexpectedly reduced"
        )

    # Test Case: #TPV-D05
    def test_remove_not_existing_human_obj(self):
        human_obj = self.create_human_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)

        response = self.remove_obj(
            url=self.detail_url,
            data=None,
            pk=99,
            token=get_valid_token_key()
        )
        self.assertNotEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "#TPV-D05: Delete operation accidentally succeed"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND,
            "#TPV-D05: Non-existing page was somehow reached"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TPV-D05: Total no. of objects is unexpectedly reduced"
        )

    # Test Case: #TPV-D06
    def test_remove_human_obj_in_wrong_url(self):
        human_obj = self.create_human_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
        num_of_cat_obj = self.get_num_of_obj(vn.CAT_VIEW_LIST)

        # Attempt to delete human instance in cat endpoint
        response = self.remove_obj(
            url=vn.CAT_VIEW_DETAIL,
            data=self.data,
            pk=human_obj.pk,
            token=get_valid_token_key()
        )
        self.assertNotEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "#TPV-D06: Delete operation accidentally succeed"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND,
            "#TPV-D06: Non-existing page was somehow reached"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TPV-D06: Total no. of objects is unexpectedly reduced"
        )
        new_num_of_cat_obj = self.get_num_of_obj(vn.CAT_VIEW_LIST)
        self.assertEqual(
            new_num_of_cat_obj, num_of_cat_obj,
            "#TPV-D06: Total no. of objects is unexpectedly reduced"
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
        self.assertEqual(
            response.json(), self.get_human_obj_url(self.new_data),
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

    # Test Case: #TPV-M05
    def test_modify_human_obj_with_invalid_data(self):
        human_obj = self.create_human_obj()

        # Generate Breed data as invalid data for Human instance
        invalid_data = factory.build(dict, FACTORY_CLASS=BreedFactory)
        response = self.modify_obj(
            url=self.detail_url,
            data=invalid_data,
            pk=human_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#TPV-M05: Able to modify human object with invalid data"
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
            "#TPV-P01: partial_modify Human object with valid token failed",

        )
        # convert http response into json for comparing purpose
        self.assertEqual(
            response.json(), self.get_human_obj_url(self.data),
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
        self.assertEqual(
            response.json(), self.get_human_obj_url(self.data),
            "#TPV-R01: Retrieve data is not same as the posted data"
        )

    # Test Case: #TPV-R02
    def test_retrieve_multiple_human_obj(self):
        human_objs = HumanFactory.create_batch(10)
        response = self.retrieve_obj(
            url=self.list_url
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TPV-R02: Retrieve human objects failed"
        )
        json_data = response.json()
        self.assertEqual(
            json_data['count'], 10,
            "#TPV-R02: Total count of human object is not correct"
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
        self.list_url = vn.CAT_VIEW_LIST
        self.detail_url = vn.CAT_VIEW_DETAIL

        # Breed and Human FKs are created before creating the Cat object
        self.breed = BreedFactory.create()
        self.owner = HumanFactory.create()
        self.data = factory.build(dict,
                                  FACTORY_CLASS=CatFactory,
                                  breed=self.breed,
                                  owner=self.owner)
        # Serve as the modifying data scheme
        self.new_data = factory.build(dict,
                                      FACTORY_CLASS=CatFactory,
                                      breed=BreedFactory.create(),
                                      owner=HumanFactory.create())
        # Parsing the cat object into acceptable dict object
        self.parse_obj(self.data, self.new_data)
        self.maxDiff = None

    def parse_obj(self, *dicts):
        for d in dicts:
            # convert FKs to hyperlinks
            d['breed'] = convert_id_to_hyperlink(vn.BREED_VIEW_DETAIL,
                                                 d['breed'])
            d['owner'] = convert_id_to_hyperlink(vn.HUMAN_VIEW_DETAIL,
                                                 d['owner'])
            # convert datetime object into str, default format(yyyy-mm-dd)
            d['date_of_birth'] = str(d['date_of_birth'])

    def create_cat_obj(self):
        data = self.data.copy()
        data['breed'] = self.breed
        data['owner'] = self.owner
        return CatFactory.create(**data)

    def get_cat_obj_url(self, data: dict):
        # Add url (hyperlink) from the cat object id to the dict object
        cat_obj = Cat.objects.latest('pk')
        data['url'] = convert_id_to_hyperlink(vn.CAT_VIEW_DETAIL, cat_obj)
        # Convert related Breed, Cat, Home id to hyperlink
        data['breed'] = convert_id_to_hyperlink(
            vn.BREED_VIEW_DETAIL, cat_obj.breed
        )
        data['owner'] = convert_id_to_hyperlink(
            vn.HUMAN_VIEW_DETAIL, cat_obj.owner
        )
        data['home'] = convert_id_to_hyperlink(
            vn.HOME_VIEW_DETAIL, cat_obj.owner.home
        )
        return data


class CatViewSetAddTests(CatViewSetBaseTests):
    '''
    Test Case Code Format: #TCV-A00

    Test cases for adding a new cat object
    '''

    # Test Case: #TCV-A01
    def test_add_cat_obj_with_valid_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED,
            "#TCV-A01: Add cat object with valid token failed"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj + 1,
            "#TCV-A01: Cat object is not added in the total count"
        )

    # Test Case: #TCV-A02
    def test_add_cat_obj_with_expired_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_expired_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-A02: Able to add cat object with expired token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TCV-A02: Invalid object is accidentally added to total count"
        )

    # Test Case: #TCV-A03
    def test_add_cat_obj_with_invalid_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
            token=get_invalid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-A03: Able to add cat object with invalid token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TCV-A03: Invalid object is accidentally added to total count"
        )

    # Test Case: #TCV-A04
    def test_add_cat_obj_without_token(self):
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.add_obj(
            url=self.list_url,
            data=self.data,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-A04: Able to add cat object without token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TCV-A04: Invalid object is accidentally added to total count"
        )

    # Test Case: #TCV-A05
    def test_add_cat_obj_in_wrong_url(self):
        num_of_cat_obj = self.get_num_of_obj(self.list_url)
        num_of_breed_obj = self.get_num_of_obj(vn.BREED_VIEW_LIST)
        # Attempt to add cat obj in breed endpoint
        response = self.add_obj(
            url=vn.BREED_VIEW_LIST,
            data=self.data,
            token=get_valid_token_key()
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#TCV-A05: Bad Request was not produced"
        )
        new_num_of_cat_obj = self.get_num_of_obj(self.list_url)
        new_num_of_breed_obj = self.get_num_of_obj(vn.BREED_VIEW_LIST)
        self.assertEqual(
            new_num_of_cat_obj, num_of_cat_obj,
            "#TCV-A05: Cat object is accidentally added to total count"
        )
        self.assertEqual(
            new_num_of_cat_obj, num_of_cat_obj,
            "#TCV-A05: Cat object is accidentally added to cat total count"
        )

    # Test Case: #TCV-A06
    def test_add_cat_obj_with_invalid_data(self):
        num_of_cat_obj = self.get_num_of_obj(self.list_url)

        # Generate Breed data as invalid data for Cat instance
        invalid_data = factory.build(dict, FACTORY_CLASS=BreedFactory)
        response = self.add_obj(
            url=self.list_url,
            data=invalid_data,
            token=get_valid_token_key()
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#TCV-A06: Able to add cat object with invalid data"
        )
        new_num_of_cat_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_cat_obj, num_of_cat_obj,
            "#TCV-A06: Cat object is accidentally added to total count"
        )


class CatViewSetDeleteTests(CatViewSetBaseTests):
    '''
    Test Case Code Format: #TCV-D00

    Test cases for removing an existing cat object
    '''

    # Test Case: #TCV-D01
    def test_remove_cat_obj_with_valid_token(self):
        cat_obj = self.create_cat_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
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
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj - 1,
            "#TCV-D01: Total count of Cat object is not reduced"
        )

    # Test Case: #TCV-D02

    def test_remove_cat_obj_with_expired_token(self):
        cat_obj = self.create_cat_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
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
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TCV-D02: Total count of Cat object is unexpectedly reduced"
        )

    # Test Case: #TCV-D03
    def test_remove_cat_obj_with_invalid_token(self):
        cat_obj = self.create_cat_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
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
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TCV-D03: Total count of Cat object is unexpectedly reduced"
        )

    # Test Case: #TCV-D04
    def test_remove_cat_obj_without_token(self):
        cat_obj = self.create_cat_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)
        response = self.remove_obj(
            url=self.detail_url,
            data=self.data,
            pk=cat_obj.pk,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED,
            "#TCV-D04: Able to remove cat object without token"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TCV-D04: Total count of Cat object is unexpectedly reduced"
        )

    # Test Case: #TCV-D05
    def test_remove_not_existing_cat_obj(self):
        CatFactory.create_batch(10)
        num_of_obj = self.get_num_of_obj(self.list_url)

        response = self.remove_obj(
            url=self.detail_url,
            data=None,
            pk=99,
            token=get_valid_token_key()
        )
        self.assertNotEqual(
            response.status_code, status.HTTP_204_NO_CONTENT,
            "#TCV-D05: Delete operation accidentally succeed"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND,
            "#TCV-D05: Non-existing page was somehow reached"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TCV-D05: Total no. of objects is unexpectedly reduced"
        )

    # Test Case: #TCV-D06
    def test_remove_cat_obj_with_wrong_pk(self):
        cat_obj = self.create_cat_obj()
        num_of_obj = self.get_num_of_obj(self.list_url)

        response = self.remove_obj(
            url=vn.BREED_VIEW_DETAIL,
            data=self.data,
            pk=99,  # wrong pk
            token=get_valid_token_key()
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND,
            "#TCV-D06: Non-existing page was somehow reached"
        )
        new_num_of_obj = self.get_num_of_obj(self.list_url)
        self.assertEqual(
            new_num_of_obj, num_of_obj,
            "#TCV-D06: Total no. of cat objects is unexpectedly reduced"
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
        self.assertEqual(
            response.json(), self.get_cat_obj_url(self.new_data),
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

    # Test Case: #TCV-M05
    def test_modify_cat_obj_with_invalid_data(self):
        cat_obj = self.create_cat_obj()

        # Generate Breed data as invalid data for Cat instance
        invalid_data = factory.build(dict, FACTORY_CLASS=BreedFactory)
        response = self.modify_obj(
            url=self.detail_url,
            data=invalid_data,
            pk=cat_obj.pk,
            token=get_valid_token_key(),
        )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST,
            "#TCV-M05: Able to modify cat object with invalid data"
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
        self.assertEqual(
            response.json(), self.get_cat_obj_url(self.data),
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
        self.assertEqual(
            response.json(), self.get_cat_obj_url(self.data),
            "#TCV-R01: Retrieve data is not same as the posted data"
        )

    # Test Case: #TCV-R02
    def test_retrieve_multiple_cat_obj(self):
        cat_objs = CatFactory.create_batch(10)
        response = self.retrieve_obj(
            url=self.list_url
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK,
            "#TCV-R02: Retrieve cat objects failed"
        )
        json_data = response.json()
        self.assertEqual(
            json_data['count'], 10,
            "#TCV-R02: Total count of cat object is not correct"
        )
