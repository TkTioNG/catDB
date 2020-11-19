from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catapp import views

app_name = 'catapp'

router = DefaultRouter()
router.register(r'breeds', views.BreedViewSet)
router.register(r'cats', views.CatViewSet)
router.register(r'homes', views.HomeViewSet)
router.register(r'humans', views.HumanViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # Expose token end point to create/renew token for registered user
    path('api-token-auth/', views.ObtainNewAuthToken.as_view()),
]
