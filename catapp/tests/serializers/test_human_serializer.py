import factory
import datetime
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse

from catapp.serializers import (
    BreedSerializer, CatSerializer, HomeSerializer, HumanSerializer
)
from catapp.factories import (
    BreedFactory, CatFactory, HomeFactory, HumanFactory
)
from catapp.models import Breed, Cat, Home, Human, Gender
from catapp.tests.base import convert_id_to_hyperlink, ViewName as vn


def make_request():
    return APIRequestFactory().get('/')


class HumanSerializerBaseTests(TestCase):
    '''
    Test Case Code Format: #TPS-X00

    Where
    =====            
        X:  A - Add
            M - Modify
            R - Retrieve
    '''

    serializer_class = HumanSerializer
    list_url = vn.HUMAN_VIEW_LIST
    detail_url = vn.HUMAN_VIEW_DETAIL

    def setUp(self):
        # home FK is created before creating the Human object
        self.home = HomeFactory.create()
        self.data = factory.build(
            dict, FACTORY_CLASS=HumanFactory, home=self.home)
        self.parse_human_dict(self.data)

        self.invalid_data = {
            'name': "*" * 31,           # More than 30 characters
            'gender': "*",              # Not in ('M', 'F', 'O')
            'date_of_birth': datetime.date.today() + datetime.timedelta(days=1),
            # Birth date in future
            'description': "*" * 301,   # More than 300 characters
            'home': BreedFactory.create()   # Invalid Home objects
        }
        self.context = {
            'request': make_request(),
        }
        self.maxDiff = None

    def create_human_obj(self):
        data = self.data.copy()
        data['home'] = self.home
        return HumanFactory.create(**data)

    def obtain_expected_result(self, data_dict, obj, read=False):
        data = dict(data_dict)
        # convert id into hyperlink
        data['url'] = convert_id_to_hyperlink(self.detail_url, obj)

        if read:
            data['name'] = obj.name
            data['gender'] = obj.gender
            data['date_of_birth'] = str(obj.date_of_birth)
            data['description'] = obj.description

        # Convert related home id to hyperlink
        data['home'] = convert_id_to_hyperlink(vn.HOME_VIEW_DETAIL, obj.home)
        data['cats'] = []
        for cat in obj.cats.all():  # Obtain all cats through Related Manager
            data['cats'].append(
                convert_id_to_hyperlink(vn.CAT_VIEW_DETAIL, cat)
            )
        data = self.sort_hyperlinks(data)

        return data

    def sort_hyperlinks(self, data: dict):
        # Sort the hyperlinks for cats field
        if data.get('cats', None):
            data['cats'] = sorted(data['cats'])
        return data

    def parse_human_dict(self, data: dict):
        # Parse Human instance dict to API standards
        data['date_of_birth'] = str(data['date_of_birth'])
        data['home'] = convert_id_to_hyperlink(
            vn.HOME_VIEW_DETAIL,
            data['home']
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
            'home': data['home']
        }


class HumanSerializerAddTests(HumanSerializerBaseTests):
    '''
    Test Case Code Format: #TPS-A00

    Test cases for adding a human object through serializer
    '''

    # Test Case: #TPS-A01
    def test_add_human_obj(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        human_obj = serializer.save()

        self.assertDictEqual(
            serializer.data,
            self.obtain_expected_result(self.data, human_obj)
        )

    # Test Case: #TPS-A02
    def test_add_human_obj_with_invalid_data(self):
        # Obtain the original number of Human objects
        num_of_obj = len(Human.objects.all())
        serializer = self.serializer_class(
            data=self.invalid_data,
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())

        # Check that all the invalid data fields are invalid
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({'name', 'gender', 'date_of_birth', 'description', 'home'})
        )
        # To make sure that the overall number of objects is the same
        new_num_of_obj = len(Human.objects.all())
        self.assertEqual(new_num_of_obj, num_of_obj)

    # Test Case: #TPS-A03
    def test_add_human_obj_with_null_data(self):
        # Obtain the original number of Human objects
        num_of_obj = len(Human.objects.all())
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
            set({'name', 'date_of_birth', 'home'})
        )
        # To make sure that the data is not added
        new_num_of_obj = len(Human.objects.all())
        self.assertEqual(new_num_of_obj, num_of_obj)

    # Test Case: #TPS-A04
    def test_add_human_obj_with_home_obj(self):
        # add related cats objects to the human object
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        human_obj = serializer.save()

        # Created related cats objects
        CatFactory.create_batch(10, owner=human_obj)
        self.assertDictEqual(
            self.sort_hyperlinks(serializer.data),
            self.obtain_expected_result(self.data, human_obj)
        )

    # Test Case: #TPS-A05
    def test_add_human_obj_with_invalid_home_obj(self):
        # Obtain the original number of Human objects
        num_of_obj = len(Human.objects.all())

        # Add invalid Home objects to the human object
        # Swap Home with Breed Object
        self.data['home'] = BreedFactory.create()
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())

        # Check that all the invalid data fields are invalid
        self.assertSetEqual(set(serializer.errors.keys()), set({'home'}))

        # To make sure that the overall number of objects is the same
        new_num_of_obj = len(Human.objects.all())
        self.assertEqual(new_num_of_obj, num_of_obj)


class HumanSerializerModifyTests(HumanSerializerBaseTests):
    '''
    Test Case Code Format: #TPS-M00

    Test cases for modifying a human object through serializer
    '''

    # Test Case: #TPS-M01
    def test_modify_human_obj(self):
        human_obj = self.create_human_obj()
        serializer = self.serializer_class(
            instance=human_obj,
            context=self.context
        )
        modified_data = factory.build(
            dict, FACTORY_CLASS=HumanFactory, home=self.home
        )
        self.parse_human_dict(modified_data)
        # Check that the new data is not the same as the old data
        self.assertNotEqual(
            self.get_required_fields(serializer.data),
            modified_data
        )
        # Update the human object
        serializer = self.serializer_class(
            instance=human_obj,
            data=modified_data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        # To check if the objects is modified
        self.assertDictEqual(
            serializer.data,
            self.obtain_expected_result(modified_data, human_obj)
        )

    # Test Case: #TPS-M02
    def test_modify_human_obj_with_invalid_data(self):
        human_obj = self.create_human_obj()
        expected_data = self.obtain_expected_result(self.data, human_obj)
        serializer = self.serializer_class(
            instance=human_obj,
            context=self.context
        )
        # Updating the instance
        serializer = self.serializer_class(
            instance=human_obj,
            data=self.invalid_data,
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())

        # Check that all the invalid data fields are invalid
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({'name', 'gender', 'date_of_birth', 'description', 'home'})
        )
        # To make sure the objects is not modified
        serializer = self.serializer_class(
            instance=human_obj,
            context=self.context
        )
        self.assertDictEqual(serializer.data, expected_data)

    # Test Case: #TPS-M03
    def test_modify_human_obj_with_null_data(self):
        human_obj = self.create_human_obj()
        expected_data = self.obtain_expected_result(self.data, human_obj)
        serializer = self.serializer_class(
            instance=human_obj,
            data={},    # null data
            context=self.context,
        )
        # To make sure that the adding of data is not valid
        self.assertFalse(serializer.is_valid())
        # To make sure that all the not null field should
        # raise error
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({'name', 'date_of_birth', 'home'})
        )
        # To make sure the objects is not modified
        serializer = self.serializer_class(
            instance=human_obj,
            context=self.context
        )
        self.assertDictEqual(serializer.data, expected_data)


class HumanSerializerRetrieveTests(HumanSerializerBaseTests):
    '''
    Test Case Code Format: #TPS-R00

    Test cases for retrieving human object through serializer
    '''

    # Test Case: #TPS-R01
    def test_contains_expected_fields(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        data = serializer.data
        self.assertEqual(
            set(data.keys()),
            set({'url', 'name', 'gender', 'date_of_birth',
                 'description', 'home', 'cats'})
        )

    # Test Case: #TPS-R02
    def test_retrieve_human_obj_one_by_one(self):
        # Create multiple humans object to retrieve
        human_objs = HumanFactory.create_batch(10)
        serializer = self.serializer_class(
            instance=human_objs,
            many=True,
            context=self.context
        )
        # Check the length of the generated serializer data
        self.assertEqual(len(serializer.data), 10)

        # Retrieve each object one by one
        for human_obj in human_objs:
            # Create cat objects to the breed objects
            CatFactory.create_batch(3, owner=human_obj)

            serializer = self.serializer_class(
                instance=human_obj,
                context=self.context
            )
            # Compare all the fields
            self.assertDictEqual(
                self.sort_hyperlinks(serializer.data),
                self.obtain_expected_result(self.data, human_obj, read=True)
            )
