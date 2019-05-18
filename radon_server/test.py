from django.http import HttpResponse


def index(request):
    response = HttpResponse("OK")
    return response
