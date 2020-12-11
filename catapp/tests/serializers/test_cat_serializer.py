import factory
import datetime
from django.test import TestCase
from rest_framework.reverse import reverse

from catapp.serializers import CatSerializer
from catapp.factories import BreedFactory, CatFactory, HomeFactory, HumanFactory
from catapp.models import Cat
from catapp.tests.base import convert_id_to_hyperlink, ViewName as vn
from catapp.tests.serializers.base import make_request


class CatSerializerBaseTests(TestCase):
    '''
    Test Case Code Format: #TCS-X00

    Where
    =====            
        X:  A - Add
            M - Modify
            R - Retrieve
    '''

    serializer_class = CatSerializer
    list_url = vn.CAT_VIEW_LIST
    detail_url = vn.CAT_VIEW_DETAIL

    def setUp(self):
        # breed and owner FK is created before creating the Cat object
        self.breed = BreedFactory.create()
        self.owner = HumanFactory.create()
        self.data = factory.build(
            dict, FACTORY_CLASS=CatFactory, breed=self.breed, owner=self.owner)
        self.parse_cat_dict(self.data)

        self.invalid_data = {
            'name': "*" * 31,           # More than 30 characters
            'gender': "*",              # Not in ('M', 'F', 'O')
            'date_of_birth': datetime.date.today() + datetime.timedelta(days=1),
            # Birth date in future
            'description': "*" * 301,   # More than 300 characters
            'breed': HomeFactory.create(),   # Invalid Breed objects
            'owner': HomeFactory.create()   # Invalid Human objects
        }
        self.context = {
            'request': make_request()
        }
        self.maxDiff = None

    def create_cat_obj(self):
        data = self.data.copy()
        data['breed'] = self.breed
        data['owner'] = self.owner
        return CatFactory.create(**data)

    def obtain_expected_result(self, data_dict, obj, read=False):
        data = dict(data_dict)
        # convert id into hyperlink
        data['url'] = convert_id_to_hyperlink(self.detail_url, obj)

        if read:
            data['name'] = obj.name
            data['gender'] = obj.gender
            data['date_of_birth'] = str(obj.date_of_birth)
            data['description'] = obj.description

        # Convert related Breed, Human, Home id to hyperlink
        data['breed'] = convert_id_to_hyperlink(
            vn.BREED_VIEW_DETAIL, obj.breed
        )
        data['owner'] = convert_id_to_hyperlink(
            vn.HUMAN_VIEW_DETAIL, obj.owner
        )
        data['home'] = convert_id_to_hyperlink(
            vn.HOME_VIEW_DETAIL, obj.owner.home
        )
        return data

    def parse_cat_dict(self, data: dict):
        # Parse Human instance dict to API standards
        data['date_of_birth'] = str(data['date_of_birth'])

        # Convert related Breed, Human, Home id to hyperlink
        data['breed'] = convert_id_to_hyperlink(
            vn.BREED_VIEW_DETAIL, data['breed']
        )
        data['owner'] = convert_id_to_hyperlink(
            vn.HUMAN_VIEW_DETAIL, data['owner']
        )
        if data.get('home', None):
            data['home'] = convert_id_to_hyperlink(
                vn.HOME_VIEW_DETAIL, data['home']
            )
        return data

    def get_required_fields(self, data: dict):
        # return required fields for comparing purpose
        # id or pk will be checked through the hyperlink format
        return {
            'name': data['name'],
            'gender': data['gender'],
            'date_of_birth': data['date_of_birth'],
            'description': data['description'],
            'breed': data['breed'],
            'owner': data['owner']
        }


class CatSerializerAddTests(CatSerializerBaseTests):
    '''
    Test Case Code Format: #TCS-A00

    Test cases for adding a cat object through serializer
    '''

    # Test Case: #TCS-A01
    def test_add_cat_obj(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        cat_obj = serializer.save()

        self.assertDictEqual(
            serializer.data,
            self.obtain_expected_result(self.data, cat_obj)
        )

    # Test Case: #TCS-A02
    def test_add_cat_obj_with_invalid_data(self):
        # Obtain the original number of Cat objects
        num_of_obj = len(Cat.objects.all())
        serializer = self.serializer_class(
            data=self.invalid_data,
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())

        # Check that all the invalid data fields are invalid
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({'name', 'gender', 'date_of_birth',
                 'description', 'breed', 'owner'})
        )
        # To make sure that the overall number of objects is the same
        new_num_of_obj = len(Cat.objects.all())
        self.assertEqual(new_num_of_obj, num_of_obj)

    # Test Case: #TCS-A03
    def test_add_cat_obj_with_null_data(self):
        # Obtain the original number of Cat objects
        num_of_obj = len(Cat.objects.all())
        serializer = self.serializer_class(
            data={},    # null data
            context=self.context
        )
        # To make sure that the adding of data is not valid
        self.assertFalse(serializer.is_valid())

        # To make sure that all the not null field should
        # raise error
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({'name', 'date_of_birth', 'breed', 'owner'})
        )
        # To make sure that the data is not added
        new_num_of_obj = len(Cat.objects.all())
        self.assertEqual(new_num_of_obj, num_of_obj)

    # Test Case: #TCS-A04
    def test_add_cat_obj_with_invalid_breed_and_human_obj(self):
        # Obtain the original number of Cat objects
        num_of_obj = len(Cat.objects.all())

        # Add invalid Breed and Human objects to the cat object
        # Swap Breed and Owner with Home Object
        self.data['breed'] = HomeFactory.create()
        self.data['owner'] = HomeFactory.create()
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())

        # Check that all the invalid data fields are invalid
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({'breed', 'owner'})
        )
        # To make sure that the overall number of objects is the same
        new_num_of_obj = len(Cat.objects.all())
        self.assertEqual(new_num_of_obj, num_of_obj)


class CatSerializerModifyTests(CatSerializerBaseTests):
    '''
    Test Case Code Format: #TCS-M00

    Test cases for modifying a cat object through serializer
    '''

    # Test Case: #TCS-M01
    def test_modify_cat_obj(self):
        cat_obj = self.create_cat_obj()
        serializer = self.serializer_class(
            instance=cat_obj,
            context=self.context
        )
        modified_data = factory.build(
            dict, FACTORY_CLASS=CatFactory, breed=self.breed, owner=self.owner
        )
        self.parse_cat_dict(modified_data)
        # Check that the new data is not the same as the old data
        self.assertNotEqual(
            serializer.data,
            self.obtain_expected_result(modified_data, cat_obj)
        )
        # Update the cat object
        serializer = self.serializer_class(
            instance=cat_obj,
            data=modified_data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        # To check if the objects is modified
        self.assertDictEqual(
            serializer.data,
            self.obtain_expected_result(modified_data, cat_obj)
        )

    # Test Case: #TCS-M02
    def test_modify_cat_obj_with_invalid_data(self):
        cat_obj = self.create_cat_obj()
        expected_data = self.obtain_expected_result(self.data, cat_obj)
        serializer = self.serializer_class(
            instance=cat_obj,
            context=self.context
        )
        # Updating the instance
        serializer = self.serializer_class(
            instance=cat_obj,
            data=self.invalid_data,
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())

        # Check that all the invalid data fields are invalid
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({'name', 'gender', 'date_of_birth',
                 'description', 'breed', 'owner'})
        )
        # To make sure the objects is not modified
        serializer = self.serializer_class(
            instance=cat_obj,
            context=self.context
        )
        self.assertDictEqual(serializer.data, expected_data)

    # Test Case: #TCS-M03
    def test_modify_cat_obj_with_null_data(self):
        cat_obj = self.create_cat_obj()
        expected_data = self.obtain_expected_result(self.data, cat_obj)
        serializer = self.serializer_class(
            instance=cat_obj,
            data={},    # null data
            context=self.context,
        )
        # To make sure that the adding of data is not valid
        self.assertFalse(serializer.is_valid())

        # To make sure that all the not null field should
        # raise error
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({'name', 'date_of_birth', 'breed', 'owner'})
        )
        # To make sure the objects is not modified
        serializer = self.serializer_class(
            instance=cat_obj,
            context=self.context
        )
        self.assertDictEqual(serializer.data, expected_data)


class CatSerializerRetrieveTests(CatSerializerBaseTests):
    '''
    Test Case Code Format: #TCS-R00

    Test cases for retrieving cat object through serializer
    '''

    # Test Case: #TCS-R01
    def test_contains_expected_fields(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.assertEqual(
            set(serializer.data.keys()),
            set({'url', 'name', 'gender', 'date_of_birth',
                 'description', 'breed', 'owner', 'home'})
        )

    # Test Case: #TCS-R02
    def test_retrieve_cat_obj_one_by_one(self):
        # Create multiple cats object to retrieve
        cat_objs = CatFactory.create_batch(10)
        for cat_obj in cat_objs:
            # Retrieve each object one by one
            serializer = self.serializer_class(
                instance=cat_obj,
                context=self.context
            )
            # Compare all the fields
            self.assertDictEqual(
                serializer.data,
                self.obtain_expected_result(self.data, cat_obj, read=True)
            )
