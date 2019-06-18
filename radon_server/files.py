import json
import os
from django.http import HttpResponse


def get_status(request):
    response = HttpResponse("OK")
    return response

def get_filelist(request, folder):
    response_data = {}
    file_list = os.listdir("radon_server/static/" + folder)
    if '.emptydir' in file_list:
        file_list.remove('.emptydir')
    response_data['file_list'] = file_list
    return HttpResponse(json.dumps(response_data), content_type="application/json")

