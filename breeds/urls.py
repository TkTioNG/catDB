from django.urls import path
from . import views

app_name = 'breeds'

urlpatterns = [
    path('', views.index, name='index'),
]
