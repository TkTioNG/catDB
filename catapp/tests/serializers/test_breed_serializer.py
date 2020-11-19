import factory
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse

from catapp.serializers import (
    BreedSerializer
)
from catapp.factories import (
    BreedFactory, CatFactory
)
from catapp.models import Breed, Cat
from catapp.tests.base import convert_id_to_hyperlink, ViewName as vn


def make_request():
    return APIRequestFactory().get('/')


class BreedSerializerBaseTests(TestCase):
    '''
    Test Case Code Format: #TBS-X00

    Where
    =====            
        X:  A - Add
            M - Modify
            R - Retrieve
    '''

    serializer_class = BreedSerializer
    list_url = vn.BREED_VIEW_LIST
    detail_url = vn.BREED_VIEW_DETAIL

    def setUp(self):
        self.data = factory.build(dict, FACTORY_CLASS=BreedFactory)
        self.invalid_data = {
            'name': "*" * 31,           # More than 30 characters
            'origin': "*" * 31,         # More than 30 characters
            'description': "*" * 301,   # More than 300 characters
        }
        self.context = {
            'request': make_request()
        }
        self.maxDiff = None

    def obtain_expected_result(self, data_dict, obj, read=False):
        data = dict(data_dict)
        # convert id into hyperlink
        data['url'] = convert_id_to_hyperlink(self.detail_url, obj)

        if read:
            data['name'] = obj.name
            data['origin'] = obj.origin
            data['description'] = obj.description

        cats = obj.cats.all()
        if cats:
            # Convert related cats and homes id to hyperlinks
            cat_hyperlinks = []
            home_hyperlinks = set()  # Use set to avoid duplicate data

            for cat in cats:
                cat_hyperlinks.append(
                    convert_id_to_hyperlink(vn.CAT_VIEW_DETAIL, cat)
                )
                home_hyperlinks.add(
                    convert_id_to_hyperlink(
                        vn.HOME_VIEW_DETAIL,
                        cat.owner.home
                    )
                )

            data['cats'] = cat_hyperlinks
            data['homes'] = home_hyperlinks
            data = self.sort_hyperlinks(data)

        else:
            # If there are no related cats,
            # the below fields should remain as empty list
            data['cats'] = []
            data['homes'] = []

        return data

    def sort_hyperlinks(self, data: dict):
        # Sort the hyperlinks for cats and homes field
        if data.get('cats', None):
            data['cats'] = sorted(data['cats'])
        if data.get('homes', None):
            data['homes'] = sorted(data['homes'])
        return data

    def get_required_fields(self, data: dict):
        # Return required fields for comparing purpose
        # id or pk will be checked through the hyperlink format
        return {
            'name': data['name'],
            'origin': data['origin'],
            'description': data['description']
        }


class BreedSerializerAddTests(BreedSerializerBaseTests):
    '''
    Test Case Code Format: #TBS-A00

    Test cases for adding a breed object through serializer
    '''

    # Test Case: #TBS-A01
    def test_add_breed_obj(self):
        num_of_obj = len(Breed.objects.all())
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        breed_obj = serializer.save()

        # Make sure that the object is serialized correctly
        self.assertDictEqual(
            serializer.data, self.obtain_expected_result(self.data, breed_obj)
        )

        # To make sure that total count of breed object is increased by 1
        new_num_of_obj = len(Breed.objects.all())
        self.assertEqual(new_num_of_obj, num_of_obj + 1)

    # Test Case: #TBS-A02
    def test_add_breed_obj_with_invalid_data(self):
        # Obtain the original number of Breed objects
        num_of_obj = len(Breed.objects.all())
        serializer = self.serializer_class(
            data=self.invalid_data,
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())

        # Check that all the invalid data fields are invalid
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({'name', 'origin', 'description'})
        )
        # To make sure that the data is not added
        breed = Breed.objects.filter(**self.invalid_data)
        self.assertEqual(len(breed), 0)

        # To make sure that the overall number of objects is the same
        new_num_of_obj = len(Breed.objects.all())
        self.assertEqual(new_num_of_obj, num_of_obj)

    # Test Case: #TBS-A03
    def test_add_breed_obj_with_not_unique_name(self):
        # name field in the Breed model should be unique
        BreedFactory.create(name=self.data['name'])
        # Obtain the original number of Breed objects
        num_of_obj = len(Breed.objects.all())
        # Create new data that has same name as above
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        # To make sure that the adding of same name is not valid
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

        # To make sure that the data is not added
        breeds = Breed.objects.filter(name=self.data['name'])
        self.assertEqual(len(breeds), 1)

        # To make sure that the overall number of objects is the same
        new_num_of_obj = len(Breed.objects.all())
        self.assertEqual(new_num_of_obj, num_of_obj)

    # Test Case: #TBS-A04
    def test_add_breed_obj_with_null_data(self):
        # Obtain the original number of Breed objects
        num_of_obj = len(Breed.objects.all())
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
            set({'name', 'origin'})
        )
        # To make sure that the overall number of objects is the same
        new_num_of_obj = len(Breed.objects.all())
        self.assertEqual(new_num_of_obj, num_of_obj)

    # Test Case: #TBS-A05
    def test_add_breed_obj_with_cats_obj(self):
        # add related cats objects to the breed object
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        breed_obj = serializer.save()

        # Created related cats objects
        CatFactory.create_batch(100, breed=breed_obj)
        self.assertDictEqual(
            self.sort_hyperlinks(serializer.data),
            self.obtain_expected_result(self.data, breed_obj)
        )
        # Noted that add invalid cats object to the breed will be
        # tested in the CatSerializerTests


class BreedSerializerModifyTests(BreedSerializerBaseTests):
    '''
    Test Case Code Format: #TBS-M00

    Test cases for modifying a breed object through serializer
    '''

    # Test Case: #TBS-M01
    def test_modify_breed_obj(self):
        breed_obj = BreedFactory.create(**self.data)
        serializer = self.serializer_class(
            instance=breed_obj,
            context=self.context
        )
        modified_data = factory.build(dict, FACTORY_CLASS=BreedFactory)

        # Check that the new data is not the same as the old data
        self.assertNotEqual(
            self.get_required_fields(serializer.data),
            modified_data
        )
        serializer = self.serializer_class(
            instance=breed_obj,
            data=modified_data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        # To check if the objects is modified
        self.assertEqual(
            serializer.data,
            self.obtain_expected_result(modified_data, breed_obj)
        )

    # Test Case: #TBS-M02
    def test_modify_breed_obj_with_invalid_data(self):
        breed_obj = BreedFactory.create(**self.data)
        serializer = self.serializer_class(
            instance=breed_obj,
            context=self.context
        )
        # Updating the instance
        serializer = self.serializer_class(
            instance=breed_obj,
            data=self.invalid_data,
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())

        # Check that all the invalid data fields are invalid
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({'name', 'origin', 'description'})
        )
        # To make sure the objects is not modified
        serializer = self.serializer_class(
            instance=breed_obj,
            context=self.context
        )
        self.assertEqual(
            serializer.data,
            self.obtain_expected_result(self.data, breed_obj)
        )

    # Test Case: #TBS-M03
    def test_modify_breed_obj_with_not_unique_name(self):
        breed_objs = BreedFactory.create_batch(2)
        # Update second breed object name same as first breed object
        serializer = self.serializer_class(
            instance=breed_objs[1],
            # Only change the name of second breed object
            data={
                'name': breed_objs[0].name,
                'origin': breed_objs[1].origin,
                'description': breed_objs[1].origin
            },
            context=self.context,
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())
        self.assertSetEqual({'name'}, set(serializer.errors.keys()))

        # To make sure that the name is not change
        breed = Breed.objects.filter(name=breed_objs[0].name)
        self.assertEqual(len(breed), 1)

    # Test Case: #TBS-M04
    def test_modify_breed_obj_with_null_data(self):
        breed_obj = BreedFactory.create(**self.data)
        serializer = self.serializer_class(
            instance=breed_obj,
            data={},    # null data
            context=self.context,
        )
        # To make sure that the adding of data is not valid
        self.assertFalse(serializer.is_valid())

        # To make sure that all the not null field should
        # raise error
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({'name', 'origin'})
        )
        # To make sure the objects is not modified
        serializer = self.serializer_class(
            instance=breed_obj,
            context=self.context
        )
        self.assertEqual(
            serializer.data,
            self.obtain_expected_result(self.data, breed_obj)
        )


class BreedSerializerRetrieveTests(BreedSerializerBaseTests):
    '''
    Test Case Code Format: #TBS-R00

    Test cases for retrieving breed object through serializer
    '''

    # Test Case: #TBS-R01
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
            set({'url', 'name', 'origin', 'description', 'cats', 'homes'})
        )

    # Test Case: #TBS-R02
    def test_retrieve_breed_obj_one_by_one(self):
        # Create multiple breeds object to retrieve
        breed_objs = BreedFactory.create_batch(10)
        serializer = self.serializer_class(
            instance=breed_objs,
            many=True,
            context=self.context
        )
        # Check the length of the generated serializer data
        self.assertEqual(len(serializer.data), 10)

        # Retrieve each object one by one
        for breed_obj in breed_objs:
            # Create cat objects to the breed objects
            CatFactory.create_batch(3, breed=breed_obj)

            serializer = self.serializer_class(
                instance=breed_obj,
                context=self.context
            )
            # Compare all the fields
            self.assertDictEqual(
                self.sort_hyperlinks(serializer.data),
                self.obtain_expected_result(self.data, breed_obj, read=True)
            )
