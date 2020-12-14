from django.urls import path, include
from rest_framework.routers import DefaultRouter

from catapp import api, views

app_name = 'catapp'

router = DefaultRouter()
router.register(r'breeds', api.BreedViewSet)
router.register(r'cats', api.CatViewSet)
router.register(r'homes', api.HomeViewSet)
router.register(r'humans', api.HumanViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.index, name='index'),
    path('breeds', views.breeds, name='breeds'),
    path('cats', views.cats, name='cats'),
    path('homes', views.homes, name='homes'),
    path('humans', views.humans, name='humans'),
    # Expose token end point to create/renew token for registered user
    path('api-token-auth/', api.ObtainNewAuthToken.as_view()),
]
