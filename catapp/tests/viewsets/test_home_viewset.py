import factory
from rest_framework import status

from catapp.models import Home
from catapp.factories import BreedFactory, HomeFactory
from catapp.tests.base import convert_id_to_hyperlink, ViewName as vn

from catapp.tests.viewsets.base import BaseTestCase, get_valid_token_key, get_expired_token_key, get_invalid_token_key


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
