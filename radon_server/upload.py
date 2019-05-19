from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm
from django.views.decorators.csrf import csrf_exempt, csrf_protect

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES['file'])
        return HttpResponseRedirect('/success/url/')
    else:
        return HttpResponseRedirect('/failure/url/')

@csrf_exempt
def handle_uploaded_file(f):
    with open('public/static/images/x.png', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
