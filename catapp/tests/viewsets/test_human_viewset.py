import factory
from rest_framework import status

from catapp.models import Cat, Human
from catapp.factories import BreedFactory,  HomeFactory, HumanFactory
from catapp.tests.base import convert_id_to_hyperlink, ViewName as vn

from catapp.tests.viewsets.base import BaseTestCase, get_valid_token_key, get_expired_token_key, get_invalid_token_key


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
