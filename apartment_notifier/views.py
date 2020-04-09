import re
from datetime import datetime
from django.http import HttpResponse
from apartment_notifier.search_apartment import search_bayernheim, search_immobilienscout

def home(request):
    return HttpResponse("Hello, Django!")

def hello_there(request, name):
    now = datetime.now()
    formatted_now = now.strftime("%A, %d %B, %Y at %X")

    # Filter the name argument to letters only using regular expressions. URL arguments
    # can contain arbitrary text, so we restrict to safe characters only.
    match_object = re.match("[a-zA-Z]+", name)

    if match_object:
        clean_name = match_object.group(0)
    else:
        clean_name = "Friend"

    content = "Hello there, " + clean_name + "! It's " + formatted_now
    return HttpResponse(content)

def find_new_places(request):
    # search_bayernheim()
    # search_immobilienscout()
    return HttpResponse("SUCCESS")

def check_bayernheim(request):
    search_bayernheim()
    return HttpResponse("SUCCESS")

def check_immoscout(request):
    search_immobilienscout()
    return HttpResponse("SUCCESS")