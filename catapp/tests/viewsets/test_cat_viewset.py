import factory
from rest_framework import status

from catapp.models import Cat
from catapp.factories import BreedFactory, CatFactory, HumanFactory
from catapp.tests.base import convert_id_to_hyperlink, ViewName as vn

from catapp.tests.viewsets.base import BaseTestCase, get_valid_token_key, get_expired_token_key, get_invalid_token_key


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
