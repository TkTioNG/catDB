from catapp.urls import app_name
from rest_framework.reverse import reverse


class ViewName:
    BREED_VIEW_LIST = app_name + ':' + 'breed-list'
    BREED_VIEW_DETAIL = app_name + ':' + 'breed-detail'
    CAT_VIEW_LIST = app_name + ':' + 'cat-list'
    CAT_VIEW_DETAIL = app_name + ':' + 'cat-detail'
    HOME_VIEW_LIST = app_name + ':' + 'home-list'
    HOME_VIEW_DETAIL = app_name + ':' + 'home-detail'
    HUMAN_VIEW_LIST = app_name + ':' + 'human-list'
    HUMAN_VIEW_DETAIL = app_name + ':' + 'human-detail'


def convert_id_to_hyperlink(view_name, obj):
    return "http://testserver" + reverse(view_name, args=[obj.id])
