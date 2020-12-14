from django.forms import ModelForm

from catapp.models import Breed, Cat, Home, Human


class BreedForm(ModelForm):
    class Meta:
        model = Breed
        fields = '__all__'
        
class CatForm(ModelForm):
    class Meta:
        model = Cat
        fields = '__all__'
        
        
class HomeForm(ModelForm):
    class Meta:
        model = Home
        fields = '__all__'
        
        
class HumanForm(ModelForm):
    class Meta:
        model = Human
        fields = '__all__'