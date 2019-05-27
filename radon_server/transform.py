from django.http import JsonResponse
from . import radon_dss

jobId = 0
threadMap = {}


def transform(request, filename):
    global jobId
    jobId += 1
    request_obj = {"requestId": jobId}
    response = JsonResponse(request_obj)
    thread = radon_dss.GetDSSRadonThread("radon_server/static/uploaded/" + filename,
                                         "radon_server/static/result/" + filename)
    thread.start()
    threadMap[jobId] = thread

    return response


def get_job_status(request, job_id):
    response = {}

    if job_id in threadMap.keys():
        thread = threadMap[job_id]

        # update running status
        if thread.progress == 0:
            response['status'] = "not started"
        elif thread.progress == 100:
            response['status'] = "completed"
        else:
            response['status'] = "running"

        response['progress'] = thread.progress
        response['took'] = thread.took
        response['targetFile'] = thread.target_file

        # save current result into file
        thread.save()

        # return status response
        return JsonResponse(response)
    else:
        return JsonResponse({"status": "unknown"})
