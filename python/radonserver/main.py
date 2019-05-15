from django.http import HttpResponse


def index(request):
    return HttpResponse("Everything is awesome")
