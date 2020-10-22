import factory
import datetime
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse

from breeds.serializers import (
    BreedSerializer, CatSerializer, HomeSerializer, HumanSerializer
)
from breeds.factories import (
    BreedFactory, CatFactory, HomeFactory, HumanFactory
)
from breeds.models import Breed, Cat, Home, Human, Gender
from .base import convert_id_to_hyperlink, ViewName as vn


def make_request():
    return APIRequestFactory().get('/')


class HomeSerializerTests(TestCase):
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
            'request': make_request(),
        }
        self.assertTrue(len(self.invalid_data['name']) > 30)
        self.assertTrue(len(self.invalid_data['address']) > 300)
        self.assertNotIn(self.invalid_data['hometype'], Home.HomeType.values)

    def obtain_expected_result(self, data, obj):
        # convert id into hyperlink
        data['url'] = convert_id_to_hyperlink(self.detail_url, obj)
        return data

    def get_required_fields(self, data: dict):
        # return required fields for comparing purpose
        # id or pk will be checked through the hyperlink format
        return {
            'name': data['name'],
            'address': data['address'],
            'hometype': data['hometype']
        }

    def test_contains_expected_fields(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.assertEqual(
            set(['url', 'name', 'address', 'hometype']),
            set(serializer.data.keys())
        )

    def test_add_home_obj(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        home_obj = serializer.save()
        expected_data = self.obtain_expected_result(self.data, home_obj)
        self.assertDictEqual(serializer.data, expected_data)

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

    def test_add_home_obj_with_null_data(self):
        # Obtain the original number of Home objects
        no_of_homes = len(Home.objects.all())
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
        new_no_of_homes = no_of_homes = len(Home.objects.all())
        self.assertEqual(new_no_of_homes, no_of_homes)

    def test_modify_home_obj(self):
        home_obj = HomeFactory.create()
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
        # To check that it is the same instance through hyperlink
        self.assertEqual(
            serializer.data['url'],
            convert_id_to_hyperlink(vn.HOME_VIEW_DETAIL, home_obj)
        )
        # To check if the objects is modified
        self.assertEqual(
            self.get_required_fields(serializer.data),
            modified_data
        )

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
            self.get_required_fields(serializer.data),
            self.data
        )

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
            self.get_required_fields(serializer.data),
            self.data
        )

    def test_retrieve_home_obj_one_by_one(self):
        # Create multiple homes object to retrieve
        home_objs = HomeFactory.create_batch(10)
        for home_obj in home_objs:
            # Retrieve each object one by one
            serializer = self.serializer_class(
                instance=home_obj,
                context=self.context
            )
            data = {
                'url': convert_id_to_hyperlink(vn.HOME_VIEW_DETAIL, home_obj),
                'name': home_obj.name,
                'address': home_obj.address,
                'hometype': home_obj.hometype,
            }
            # Compare all the fields
            self.assertDictEqual(
                serializer.data,
                data
            )

    def test_retrieve_multiple_home_objs(self):
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
            # To check that it is the same instance
            self.assertEqual(
                serializer_data['url'],
                convert_id_to_hyperlink(vn.HOME_VIEW_DETAIL, home_obj)
            )
            data = {
                'name': home_obj.name,
                'address': home_obj.address,
                'hometype': home_obj.hometype,
            }
            # Compare all the fields
            self.assertDictEqual(
                self.get_required_fields(serializer_data),
                data
            )


class BreedSerializerTests(TestCase):
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
            'request': make_request(),
        }
        self.maxDiff = None

    def obtain_expected_result(self, data_dict, obj, cats=None):
        data = dict(data_dict)
        # convert id into hyperlink
        data['url'] = convert_id_to_hyperlink(self.detail_url, obj)
        data['name'] = obj.name
        data['origin'] = obj.origin
        data['description'] = obj.description

        if cats:
            # Convert related cats and homes id to hyperlinks
            cat_hyperlinks = []
            home_hyperlinks = set()  # Use set to avoid duplicate data
            # Sort cat objects based on the Cat model ordering method
            for cat in cats:  # sorted(cats, key=lambda c: c.name)
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
            data['homes'] = home_hyperlinks  # convert back to list
            data = self.sort_hyperlinks(data)

        else:
            # If no realted cats, the below fields should be empty list
            data['cats'] = []
            data['homes'] = []

        return data

    def sort_hyperlinks(self, data: dict):
        if data.get('cats', None):
            data['cats'] = sorted(data['cats'])
        if data.get('homes', None):
            data['homes'] = sorted(data['homes'])
        return data

    def get_required_fields(self, data: dict):
        # return required fields for comparing purpose
        # id or pk will be checked through the hyperlink format
        return {
            'name': data['name'],
            'origin': data['origin'],
            'description': data['description']
        }

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
            set(['url', 'name', 'origin', 'description', 'cats', 'homes'])
        )

    def test_add_breed_obj(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        breed_obj = serializer.save()
        expected_data = self.obtain_expected_result(self.data, breed_obj)
        self.assertDictEqual(serializer.data, expected_data)

    def test_add_breed_obj_with_invalid_data(self):
        # Obtain the original number of Breed objects
        no_of_breeds = len(Breed.objects.all())
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
        self.assertEqual(len(breed), 0)  # Check that no result filtered
        # To make sure that the overall number of objects is the same
        new_no_of_breeds = len(Breed.objects.all())
        self.assertEqual(new_no_of_breeds, no_of_breeds)

    def test_add_breed_obj_with_not_unique_name(self):
        # name field in the Breed model should be unique
        BreedFactory.create(name=self.data['name'])
        # Obtain the original number of Breed objects
        no_of_breeds = len(Breed.objects.all())
        serializer = self.serializer_class(
            data=self.data,  # data with same name as above
            context=self.context
        )
        # To make sure that the adding of same name is not valid
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

        # To make sure that the data is not added
        breeds = Breed.objects.filter(name=self.data['name'])
        self.assertEqual(len(breeds), 1)
        # To make sure that the overall number of objects is the same
        new_no_of_breeds = len(Breed.objects.all())
        self.assertEqual(new_no_of_breeds, no_of_breeds)

    def test_add_breed_obj_with_null_data(self):
        # Obtain the original number of Breed objects
        no_of_breeds = len(Breed.objects.all())
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
        new_no_of_breeds = len(Breed.objects.all())
        self.assertEqual(new_no_of_breeds, no_of_breeds)

    def test_add_breed_obj_with_cats_obj(self):
        # add related cats objects to the breed object
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        breed_obj = serializer.save()
        # Created related cats objects
        cats = CatFactory.create_batch(100, breed=breed_obj)
        expected_data = self.obtain_expected_result(
            self.data, breed_obj, cats=cats
        )
        self.assertDictEqual(
            self.sort_hyperlinks(serializer.data),
            expected_data
        )
        # Noted that add invalid cats object to the breed will be
        # tested in the CatSerializerTests

    def test_modify_breed_obj(self):
        breed_obj = BreedFactory.create()
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
        # To check that it is the same instance
        self.assertEqual(
            serializer.data['url'],
            convert_id_to_hyperlink(vn.BREED_VIEW_DETAIL, breed_obj)
        )
        # To check if the objects is modified
        self.assertEqual(
            self.get_required_fields(serializer.data),
            modified_data
        )

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
            self.get_required_fields(serializer.data),
            self.data
        )

    def test_retrieve_breed_obj_one_by_one(self):
        # Create multiple breeds object to retrieve
        breed_objs = BreedFactory.create_batch(10)
        for breed_obj in breed_objs:
            # Retrieve each object one by one
            # Create cat objects to the breed objects
            cats = CatFactory.create_batch(3, breed=breed_obj)
            serializer = self.serializer_class(
                instance=breed_obj,
                context=self.context
            )
            self.data = {
                'name': breed_obj.name,
                'origin': breed_obj.origin,
                'description': breed_obj.description,
            }
            expected_data = self.obtain_expected_result(
                self.data, breed_obj, cats=cats
            )
            # Compare all the fields
            self.assertDictEqual(
                self.sort_hyperlinks(serializer.data),
                expected_data
            )


class HumanSerializerTests(TestCase):
    serializer_class = HumanSerializer
    list_url = vn.HUMAN_VIEW_LIST
    detail_url = vn.HUMAN_VIEW_DETAIL

    def setUp(self):
        self.data = factory.build(dict, FACTORY_CLASS=HumanFactory)
        self.data['date_of_birth'] = str(self.data['date_of_birth'])
        self.data['home'] = convert_id_to_hyperlink(
            vn.HOME_VIEW_DETAIL,
            HomeFactory.create()
        )
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
        self.fields = {
            'url',
            'name',
            'gender',
            'date_of_birth',
            'description',
            'home',
            'cats'
        }
        self.maxDiff = None

    def obtain_expected_result(self, data_dict, obj):
        data = dict(data_dict)
        # convert id into hyperlink
        data['url'] = convert_id_to_hyperlink(self.detail_url, obj)
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

    def test_contains_expected_fields(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        data = serializer.data
        self.assertEqual(set(data.keys()), set(self.fields))

    def test_add_human_obj(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        human_obj = serializer.save()
        expected_data = self.obtain_expected_result(self.data, human_obj)
        self.assertDictEqual(serializer.data, expected_data)

    def test_add_human_obj_with_invalid_data(self):
        # Obtain the original number of Human objects
        no_of_humans = len(Human.objects.all())
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
        new_no_of_humans = len(Human.objects.all())
        self.assertEqual(new_no_of_humans, no_of_humans)

    def test_add_human_obj_with_null_data(self):
        # Obtain the original number of Human objects
        no_of_humans = len(Human.objects.all())
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
        new_no_of_humans = len(Human.objects.all())
        self.assertEqual(new_no_of_humans, no_of_humans)

    def test_add_human_obj_with_home_obj(self):
        # add related cats objects to the human object
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        human_obj = serializer.save()
        # Created related cats objects
        expected_data = self.obtain_expected_result(self.data, human_obj)
        self.assertDictEqual(serializer.data, expected_data)

    def test_add_human_obj_with_invalid_home_obj(self):
        # Obtain the original number of Human objects
        no_of_humans = len(Human.objects.all())
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
        new_no_of_humans = len(Human.objects.all())
        self.assertEqual(new_no_of_humans, no_of_humans)

    def test_modify_human_obj(self):
        human_obj = HumanFactory.create()
        serializer = self.serializer_class(
            instance=human_obj,
            context=self.context
        )
        # Check that the new data is not the same as the old data
        self.assertNotEqual(
            self.get_required_fields(serializer.data),
            self.data
        )
        # Update the human object
        serializer = self.serializer_class(
            instance=human_obj,
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        # To check that it is the same instance
        self.assertEqual(
            serializer.data['url'],
            convert_id_to_hyperlink(vn.HUMAN_VIEW_DETAIL, human_obj)
        )
        # To check if the objects is modified
        self.assertDictEqual(
            self.get_required_fields(serializer.data),
            self.data
        )

    def test_modify_human_obj_with_invalid_data(self):
        human_obj = HumanFactory.create()
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

    def test_modify_human_obj_with_null_data(self):
        human_obj = HumanFactory.create()
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

    def test_retrieve_human_obj_one_by_one(self):
        # Create multiple humans object to retrieve
        human_objs = HumanFactory.create_batch(10)
        for human_obj in human_objs:
            # Retrieve each object one by one
            serializer = self.serializer_class(
                instance=human_obj,
                context=self.context
            )
            expected_data = self.obtain_expected_result(self.data, human_obj)
            # Compare all the fields
            self.assertDictEqual(serializer.data, expected_data)


class CatSerializerTests(TestCase):
    serializer_class = CatSerializer
    list_url = vn.CAT_VIEW_LIST
    detail_url = vn.CAT_VIEW_DETAIL

    def setUp(self):
        self.data = factory.build(dict, FACTORY_CLASS=CatFactory)
        self.data['date_of_birth'] = str(self.data['date_of_birth'])
        self.data['breed'] = convert_id_to_hyperlink(
            vn.BREED_VIEW_DETAIL,
            BreedFactory.create()
        )
        self.data['owner'] = convert_id_to_hyperlink(
            vn.HUMAN_VIEW_DETAIL,
            HumanFactory.create()
        )
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
            'request': make_request(),
        }
        self.fields = {
            'url',
            'name',
            'gender',
            'date_of_birth',
            'description',
            'breed',
            'owner',
            'home'
        }
        self.maxDiff = None

    def obtain_expected_result(self, data_dict, obj):
        data = dict(data_dict)
        # convert id into hyperlink
        data['url'] = convert_id_to_hyperlink(self.detail_url, obj)
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

    def test_contains_expected_fields(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        data = serializer.data
        self.assertEqual(set(data.keys()), set(self.fields))

    def test_add_cat_obj(self):
        serializer = self.serializer_class(
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        cat_obj = serializer.save()
        expected_data = self.obtain_expected_result(self.data, cat_obj)
        self.assertDictEqual(serializer.data, expected_data)

    def test_add_cat_obj_with_invalid_data(self):
        # Obtain the original number of Cat objects
        no_of_cats = len(Cat.objects.all())
        serializer = self.serializer_class(
            data=self.invalid_data,
            context=self.context
        )
        # To make sure that the data is invalid
        self.assertFalse(serializer.is_valid())
        # Check that all the invalid data fields are invalid
        self.assertSetEqual(
            set(serializer.errors.keys()),
            set({
                'name',
                'gender',
                'date_of_birth',
                'description',
                'breed',
                'owner'
            })
        )
        # To make sure that the overall number of objects is the same
        new_no_of_cats = len(Cat.objects.all())
        self.assertEqual(new_no_of_cats, no_of_cats)

    def test_add_cat_obj_with_null_data(self):
        # Obtain the original number of Cat objects
        no_of_cats = len(Cat.objects.all())
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
        new_no_of_cats = len(Cat.objects.all())
        self.assertEqual(new_no_of_cats, no_of_cats)

    def test_add_cat_obj_with_invalid_breed_and_human_obj(self):
        # Obtain the original number of Cat objects
        no_of_cats = len(Cat.objects.all())
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
        new_no_of_cats = len(Cat.objects.all())
        self.assertEqual(new_no_of_cats, no_of_cats)

    def test_modify_cat_obj(self):
        cat_obj = CatFactory.create()
        serializer = self.serializer_class(
            instance=cat_obj,
            context=self.context
        )
        # Check that the new data is not the same as the old data
        self.assertNotEqual(
            self.get_required_fields(serializer.data),
            self.data
        )
        # Update the cat object
        serializer = self.serializer_class(
            instance=cat_obj,
            data=self.data,
            context=self.context
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        # To check that it is the same instance
        self.assertEqual(
            serializer.data['url'],
            convert_id_to_hyperlink(vn.CAT_VIEW_DETAIL, cat_obj)
        )
        # To check if the objects is modified
        self.assertDictEqual(
            self.get_required_fields(serializer.data),
            self.data
        )

    def test_modify_cat_obj_with_invalid_data(self):
        cat_obj = CatFactory.create()
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
            set({
                'name',
                'gender',
                'date_of_birth',
                'description',
                'breed',
                'owner'
            })
        )
        # To make sure the objects is not modified
        serializer = self.serializer_class(
            instance=cat_obj,
            context=self.context
        )
        self.assertDictEqual(serializer.data, expected_data)

    def test_modify_cat_obj_with_null_data(self):
        cat_obj = CatFactory.create()
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

    def test_retrieve_cat_obj_one_by_one(self):
        # Create multiple cats object to retrieve
        cat_objs = CatFactory.create_batch(10)
        for cat_obj in cat_objs:
            # Retrieve each object one by one
            serializer = self.serializer_class(
                instance=cat_obj,
                context=self.context
            )
            expected_data = self.obtain_expected_result(self.data, cat_obj)
            # Compare all the fields
            self.assertDictEqual(serializer.data, expected_data)
