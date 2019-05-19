from django.http import HttpResponse
import json

def get_status(request):
    response = HttpResponse("OK")
    return response

def get_filelist(request):
    response_data = {}
    file_list = ["static/images/phantom128x128.png", "static/images/lenna128x128.png"]
    response_data['file_list'] = file_list
    return HttpResponse(json.dumps(response_data), content_type="application/json")

