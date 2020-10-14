from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'breeds'

router = DefaultRouter()
router.register(r'breeds', views.BreedViewSet)
router.register(r'cats', views.CatViewSet)
router.register(r'homes', views.HomeViewSet)
router.register(r'humans', views.HumanViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
]
