import factory
from rest_framework import status

from catapp.models import Breed, Cat
from catapp.factories import BreedFactory, HomeFactory
from catapp.tests.base import convert_id_to_hyperlink, ViewName as vn

from catapp.tests.viewsets.base import BaseTestCase, get_valid_token_key, get_expired_token_key, get_invalid_token_key


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
