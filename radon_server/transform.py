from django.http import JsonResponse
from . import radon_dss
from . import radon_pbim
from . import radon_shas
from . import radon_twoscale
from . import radon_sss
from . import radon_fss

jobId = 0
threadMap = {}


# noinspection PyUnusedLocal
def transform(request, algorithm, filename):
    global jobId
    jobId += 1
    request_obj = {"requestId": jobId}
    target_filename = filename[:-3] + algorithm + "." + filename[-3:]
    source = "radon_server/static/uploaded/" + filename
    target = "radon_server/static/result/" + target_filename
    request_obj["target"] = target_filename

    if algorithm == "dss":
        thread = radon_dss.DSSRadon(source, target)
    elif algorithm == "pbim":
        thread = radon_pbim.PBIMTransform(source, target)
    elif algorithm == "shas":
        thread = radon_shas.SHASTransform(source, target)
    elif algorithm == "twoscale":
        thread = radon_twoscale.TwoScaleTransform(source, target)
    elif algorithm == "sss":
        thread = radon_sss.SlowSlantStackTransform(source, target)
    elif algorithm == "fss":
        thread = radon_fss.FastSlantStackTransform(source, target)
    else:
        return JsonResponse({"error": "Unsupported Algorithm"})

    thread.start()
    threadMap[jobId] = thread

    return JsonResponse(request_obj)


# noinspection PyUnusedLocal
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
