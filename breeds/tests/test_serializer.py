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
    
    def parse_human_dict(self, data:dict):
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
    
    def parse_cat_dict(self, data:dict):
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
