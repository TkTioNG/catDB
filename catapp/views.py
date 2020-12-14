from django.shortcuts import render
import requests
import re

from catapp.forms import BreedForm, CatForm, HomeForm, HumanForm
from catapp.models import Breed, Cat, Home, Human


HEADERS = {
    'Authorization': 'Token 19fc7a06d165fd0d2b38f0d00c2d72d8ebbf55b9'
}


def index(request):
    return render(request, 'catapp/index.html')


def breeds(request):
    context = {}
    if request.method == "POST":
        form_data = request.POST
        post_data = {
            "name": form_data.get("name"),
            "origin": form_data.get("origin"),
            "description": form_data.get("description")
        }
        post_req = requests.post(
            'http://localhost:8000/catapp/api/breeds/',
            post_data,
            headers=HEADERS
        )
        if post_req.status_code == 201:
            context["success"] = True
        else:
            context["errors"] = post_req.json()
            
    req = requests.get(
        'http://localhost:8000/catapp/api/breeds',
        headers=HEADERS
    )
    if req.status_code == 200:
        context['breeds'] = req.json().get('results', [])
        context['form'] = BreedForm()
    else:
        context['errors'] = req.json()
    return render(request, 'catapp/breeds.html', context)


def cats(request):
    context = {}
    if request.method == "POST":
        form_data = request.POST
        post_data = {
            "name": form_data.get("name"),
            "gender": form_data.get("gender"),
            "date_of_birth": "2020-12-01",
            "description": form_data.get("description"),
            "breed": "http://localhost:8000/catapp/api/breeds/" + form_data.get("breed") + "/",
            "owner": "http://localhost:8000/catapp/api/humans/" + form_data.get("owner") + "/",
        }
        post_req = requests.post(
            'http://localhost:8000/catapp/api/cats/',
            post_data,
            headers=HEADERS
        )
        if post_req.status_code == 201:
            context["success"] = True
        else:
            context["errors"] = post_req.json()
        
    req = requests.get(
        'http://localhost:8000/catapp/api/cats',
        headers=HEADERS
    )
    if req.status_code == 200:
        all_cats = req.json().get('results', [])
        for cat in all_cats:
            breed = Breed.objects.get(pk=int(re.split('/', cat.get('breed'))[-2])).name
            owner = Human.objects.get(pk=int(re.split('/', cat.get('owner'))[-2])).name
            
            cat['breed'] = breed
            cat['owner'] = owner
        
        context['cats'] = all_cats
        
    else:
        context['errors'] = req.json()
        
    context['form'] = CatForm()
    
    print(context)
        
    return render(request, 'catapp/cats.html', context)


def homes(request):
    context = {}
    if request.method == "POST":
        form_data = request.POST
        post_data = {
            "name": form_data.get("name"),
            "address": form_data.get("address"),
            "hometype": form_data.get("hometype")
        }
        post_req = requests.post(
            'http://localhost:8000/catapp/api/homes/',
            post_data,
            headers=HEADERS
        )
        if post_req.status_code == 201:
            context["success"] = True
        else:
            context["errors"] = post_req.json()
            
    req = requests.get(
        'http://localhost:8000/catapp/api/homes',
        headers=HEADERS
    )
    if req.status_code == 200:
        context['homes'] = req.json().get('results', [])
        context['form'] = HomeForm()
    else:
        context['errors'] = req.json()
        
    return render(request, 'catapp/homes.html', context)

def humans(request):
    context = {}
    if request.method == "POST":
        form_data = request.POST
        post_data = {
            "name": form_data.get("name"),
            "gender": form_data.get("gender"),
            "date_of_birth": "2020-12-01",
            "description": form_data.get("description"),
            "home": "http://localhost:8000/catapp/api/homes/" + form_data.get("home") + "/",
        }
        post_req = requests.post(
            'http://localhost:8000/catapp/api/humans/',
            post_data,
            headers=HEADERS
        )
        if post_req.status_code == 201:
            context["success"] = True
        else:
            context["errors"] = post_req.json()
            
    req = requests.get(
        'http://localhost:8000/catapp/api/humans',
        headers=HEADERS
    )
    if req.status_code == 200:
        all_humans = req.json().get('results', [])
        for human in all_humans:
            home = Home.objects.get(pk=int(re.split('/', human.get('home'))[-2])).name
            human['home'] = home
            
        context['humans'] = all_humans
        context['form'] = HumanForm()
    else:
        context['errors'] = req.json()
    return render(request, 'catapp/humans.html', context)