from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(response):
    return HttpResponse("buy sell buy sell")
def about(response):
    return HttpResponse("This is the about page")   