from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.contrib import messages
from django.urls import path

from .forms import LoginForm, RegistrationForm



# Create your views here.


def index(response):
    return HttpResponse("buy sell buy sell")
def about(request):
    return render(request, 'about.html') 
def contact(request):
    return render(request, 'contact.html') 

# Registration
def register(request):
    if request.method == 'GET':
        form = RegistrationForm()
        return render(request, 'registration/register.html', {'form': form})    
   
    if request.method == 'POST':
        form = RegistrationForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'You have singed up successfully.')
            login(request, user)
            return redirect('posts')
        else:
            return render(request, 'registration/register.html', {'form': form})




