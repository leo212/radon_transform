from django.http import HttpResponse


def index():
    response = HttpResponse("OK")
    return response
