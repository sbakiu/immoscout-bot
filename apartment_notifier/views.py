import re
from datetime import datetime
from django.http import HttpResponse
from apartment_notifier.search_apartment import search_bayernheim, search_immobilienscout

def home(request):
    return HttpResponse("Hello, Django!")

def hello_there(request):
    return HttpResponse("HELLO")

def find_new_places(request):
    search_bayernheim()
    search_immobilienscout()
    return HttpResponse("SUCCESS")

def check_bayernheim(request):
    search_bayernheim()
    return HttpResponse("SUCCESS")

def check_immoscout(request):
    search_immobilienscout()
    return HttpResponse("SUCCESS")