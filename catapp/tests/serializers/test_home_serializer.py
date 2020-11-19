import factory
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse

from catapp.serializers import (
    HomeSerializer
)
from catapp.factories import (
    HomeFactory
)
from catapp.models import Home
from catapp.tests.base import convert_id_to_hyperlink, ViewName as vn


def make_request():
    return APIRequestFactory().get('/')


class HomeSerializerBaseTests(TestCase):
    '''
    Test Case Code Format: #THS-X00

    Where
    =====            
        X:  A - Add
            M - Modify
            R - Retrieve
    '''

    serializer_class = HomeSerializer
    list_url = vn.HOME_VIEW_LIST
    detail_url = vn.HOME_VIEW_DETAIL

    def setUp(self):
        self.data = factory.build(dict, FACTORY_CLASS=HomeFactory)
        self.invalid_data = {
            'name': "*" * 31,       # More than 30 characters
            'address': "*" * 301,   # More than 300 characters
            'hometype': "unknown",  # Not in ['landed', 'condominium']
        }
        self.context = {
            'request': make_request()
        }
        self.assertTrue(len(self.invalid_data['name']) > 30)
        self.assertTrue(len(self.invalid_data['address']) > 300)
        self.assertNotIn(self.invalid_data['hometype'], Home.HomeType.values)

    def obtain_expected_result(self, data, obj, read=False):
        """
        Convert Home object id into hyperlink for hyperlink related field

        Args:        
            data (dict): data of the Home object.                        
            obj (Home): Home object instance.                        
            read (bool, optional): IF True copy the obj data to the data dict. 
                                   Defaults to False.

        Returns:
            dict : Home object data with hyperlink related field
        """

        # convert id into hyperlink
        data['url'] = convert_id_to_hyperlink(self.detail_url, obj)

        if read:
            data['name'] = obj.name
            data['address'] = obj.address
            data['hometype'] = obj.hometype

        return data

    def get_required_fields(self, data: dict):
        """
        Return required fields for comparing purpose.

        Args:
            data (dict): dict object that contains Home instance data

        Returns:
            dict: dict object that contains required fields of Home instance
        """

        return {
            'name': data['name'],
            'address': data['address'],
            'hometype': data['hometype']
        }


class HomeSerializerAddTests(HomeSerializerBaseTests):
    '''
    Test Case Code Format: #THS-A00

    Test cases for adding a new home object through serializer
    '''

    # Test Case: #THS-A01
    def test_add_home_obj(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        home_obj = serializer.save()

        self.assertDictEqual(
            serializer.data,
            self.obtain_expected_result(self.data, home_obj)
        )

    # Test Case: #THS-A02
    def test_add_home_obj_with_invalid_data(self):
        serializer = self.serializer_class(
            data=self.invalid_data,
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())

        # Check that all the invalid data fields are invalid
        self.assertSetEqual(
            set({'name', 'address', 'hometype'}),
            set(serializer.errors.keys())
        )
        # To make sure that the data is not added
        home = Home.objects.filter(**self.invalid_data)
        self.assertEqual(len(home), 0)  # Check that no result filtered

    # Test Case: #THS-A03
    def test_add_home_obj_with_null_data(self):
        # Obtain the original number of Home objects
        num_of_obj = len(Home.objects.all())
        serializer = self.serializer_class(
            data={},    # null data
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())

        # To make sure that all the not null field should
        # raise error
        self.assertSetEqual(
            set({'name', 'address', 'hometype'}),
            set(serializer.errors.keys())
        )
        # To make sure that the overall number of objects is the same
        new_num_of_obj = num_of_obj = len(Home.objects.all())
        self.assertEqual(new_num_of_obj, num_of_obj)


class HomeSerializerModifyTests(HomeSerializerBaseTests):
    '''
    Test Case Code Format: #THS-M00

    Test cases for modifying a new home object through serializer
    '''

    # Test Case: #THS-M01
    def test_modify_home_obj(self):
        home_obj = HomeFactory.create(**self.data)
        serializer = self.serializer_class(
            instance=home_obj,
            context=self.context
        )
        # Create new data that is not same as the original data
        modified_data = factory.build(dict, FACTORY_CLASS=HomeFactory)
        self.assertNotEqual(
            self.get_required_fields(serializer.data),
            modified_data
        )
        # Updating the instance
        serializer = self.serializer_class(
            instance=home_obj,
            data=modified_data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        # To check if the objects is modified
        self.assertEqual(
            serializer.data,
            self.obtain_expected_result(modified_data, home_obj)
        )

    # Test Case: #THS-M02
    def test_modify_home_obj_with_invalid_data(self):
        home_obj = HomeFactory.create(**self.data)
        # Retrieve the created home object
        serializer = self.serializer_class(
            instance=home_obj,
            context=self.context
        )
        # Updating the instance
        serializer = self.serializer_class(
            instance=home_obj,
            data=self.invalid_data,
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())

        # Check that all the invalid data fields are invalid
        self.assertSetEqual(
            set({'name', 'address', 'hometype'}),
            set(serializer.errors.keys())
        )
        # To make sure the objects is not modified
        serializer = self.serializer_class(
            instance=home_obj,
            context=self.context
        )
        self.assertEqual(
            serializer.data,
            self.obtain_expected_result(self.data, home_obj)
        )

    # Test Case: #THS-M03
    def test_modify_home_obj_with_null_data(self):
        home_obj = HomeFactory.create(**self.data)
        serializer = self.serializer_class(
            instance=home_obj,
            data={},    # null data
            context=self.context,
        )
        # To make sure that the adding of data is not valid
        self.assertFalse(serializer.is_valid())

        # To make sure that all the not null field should
        # raise error
        self.assertSetEqual(
            {'name', 'address', 'hometype'},
            set(serializer.errors.keys())
        )
        # To make sure the objects is not modified
        serializer = self.serializer_class(
            instance=home_obj,
            context=self.context
        )
        self.assertEqual(
            serializer.data,
            self.obtain_expected_result(self.data, home_obj)
        )


class HomeSerializerRetrieveTests(HomeSerializerBaseTests):
    '''
    Test Case Code Format: #THS-R00

    Test cases for retrieving home object through serializer
    '''

    # Test Case: #THS-R01
    def test_contains_expected_fields(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.assertEqual(
            set({'url', 'name', 'address', 'hometype'}),
            set(serializer.data.keys())
        )

    # Test Case: #THS-R02
    def test_retrieve_home_obj_one_by_one(self):
        # Create multiple homes object to retrieve
        home_objs = HomeFactory.create_batch(10)
        serializer = self.serializer_class(
            instance=home_objs,
            many=True,
            context=self.context
        )
        # Check the length of the generated serializer data
        self.assertEqual(len(serializer.data), 10)

        # Compare the data one by one
        for home_obj, serializer_data in zip(home_objs, serializer.data):
            # Compare all the fields to make the the home object is
            # serialize correctly
            self.assertDictEqual(
                serializer_data,
                self.obtain_expected_result({}, home_obj, read=True)
            )
