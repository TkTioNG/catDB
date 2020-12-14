from django.contrib import admin

from catapp.models import Breed, Cat, Home, Human

@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    pass

@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    pass


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    pass


@admin.register(Human)
class HumanAdmin(admin.ModelAdmin):
    pass
