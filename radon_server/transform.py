from django.http import HttpResponse

from . import radon_dss


def index():
    radon_dss.test_dss("images/lenna128x128.png")
    response = HttpResponse("OK")
    return response
