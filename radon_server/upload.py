from django.http import HttpResponse,HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES['file'])
        return HttpResponse("OK")
    else:
        return HttpResponseServerError("Error uploading file")

@csrf_exempt
def handle_uploaded_file(f):
    with open('radon_server/static/uploaded/' + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
