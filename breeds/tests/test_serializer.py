import factory
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse

from breeds.serializers import (
    BreedSerializer, CatSerializer, HomeSerializer, HumanSerializer
)
from breeds.factories import (
    BreedFactory, CatFactory, HomeFactory, HumanFactory
)
from .base import ViewName as vn


def make_request():
    return APIRequestFactory().get('/')


def convert_id_to_hyperlink(view_name, obj):
    return "http://testserver" + reverse(view_name, args=[obj.id])


class BreedSerializerTests(TestCase):
    serializer_class = BreedSerializer
    list_url = vn.BREED_VIEW_LIST
    detail_url = vn.BREED_VIEW_DETAIL

    def setUp(self):
        self.data = factory.build(dict, FACTORY_CLASS=BreedFactory)
        self.context = {
            'request': make_request(),
        }

    def obtain_expected_result(self, data_dict, obj, cats=None):
        data = dict(data_dict)
        # convert id into hyperlink
        data['url'] = convert_id_to_hyperlink(self.detail_url, obj)

        if cats:
            cat_hyperlinks = []
            homes = set()  # Use set to avoid duplicate data
            # Sort cat objects based on the Cat model ordering method
            for cat in sorted(cats, key=lambda c: c.name):
                cat_hyperlinks.append(
                    convert_id_to_hyperlink(vn.CAT_VIEW_DETAIL, cat)
                )
                homes.add(cat.owner.home)

            home_hyperlinks = []
            # Sort home objects based on the Home model ordering method
            for home in sorted(homes, key=lambda h: h.id):
                home_hyperlinks.append(
                    convert_id_to_hyperlink(vn.HOME_VIEW_DETAIL, home)
                )
            data['cats'] = cat_hyperlinks
            data['homes'] = home_hyperlinks

        else:
            # If no realted cats, the below fields should be empty list
            data['cats'] = []
            data['homes'] = []

        return data

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
            set(['url', 'name', 'origin', 'description', 'cats', 'homes']),
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

    def test_add_breed_obj_with_cats_obj(self):
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
        self.assertDictEqual(serializer.data, expected_data)

    def test_modify_breed_obj(self):
        breed_obj = BreedFactory.create()
        serializer = self.serializer_class(
            instance=breed_obj,
            context=self.context
        )

        modified_data = factory.build(dict, FACTORY_CLASS=BreedFactory)
        self.assertNotEqual(
            {
                'name': serializer.data['name'],
                'origin': serializer.data['origin'],
                'description': serializer.data['description'],
            }, modified_data
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
            {
                'name': serializer.data['name'],
                'origin': serializer.data['origin'],
                'description': serializer.data['description'],
            }, modified_data
        )

    def test_retrieve_breed_objs(self):
        self.maxDiff = None
        breed_objs = BreedFactory.create_batch(10)
        for breed_obj in breed_objs:
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
            self.assertSetEqual(
                set(serializer.data['cats']), set(expected_data['cats'])
            )
            self.assertSetEqual(
                set(serializer.data['homes']), set(expected_data['homes'])
            )
            
