from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_views
from . import views

app_name = 'breeds'

router = DefaultRouter()
router.register(r'breeds', views.BreedViewSet)
router.register(r'cats', views.CatViewSet)
router.register(r'homes', views.HomeViewSet)
router.register(r'humans', views.HumanViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # Expose token end point to create token for registered user
    path('api-token-auth/', auth_views.obtain_auth_token),
]
# TODO: Create end point that can renew the token  