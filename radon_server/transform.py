import math
import os
import time

from django.http import JsonResponse
from . import radon_dss
from . import radon_pbim
from . import radon_shas
from . import radon_twoscale
from . import radon_sss
from . import radon_fss
from .radon_thread import get_matrix_filename

jobId = 0
threadMap = {}
algorithms = {"dss": radon_dss.DSSRadon,
              "pbim": radon_pbim.PBIMTransform,
              "shas": radon_shas.SHASTransform,
              "twoscale": radon_twoscale.TwoScaleTransform,
              "sss": radon_sss.SlowSlantStackTransform,
              "fss": radon_fss.FastSlantStackTransform}


# noinspection PyUnusedLocal
def transform(request, algorithm, variant, filename):
    global jobId
    global algorithms
    jobId += 1
    request_obj = {"requestId": jobId}
    target_filename = filename[:-3] + algorithm + "." + variant + "." + filename[-3:]
    source = "radon_server/static/uploaded/" + filename
    target_image = "radon_server/static/result/" + target_filename
    target_file = "radon_server/static/radon/" + filename[:-3] + algorithm + "." + variant
    request_obj["target"] = target_filename

    if algorithm in algorithms:
        args = {"source_file": source, "target_file": target_file, "target_image": target_image}
        thread = algorithms[algorithm](action="transform", variant=variant, args=args)
    else:
        return JsonResponse({"error": "Unsupported Algorithm: " + algorithm})

    thread.start()
    thread.started = True
    threadMap[jobId] = thread

    return JsonResponse(request_obj)


# noinspection PyUnusedLocal
def build_matrix(request, algorithm, variant, size):
    global jobId
    jobId += 1
    request_obj = {"requestId": jobId}
    if algorithm in algorithms:
        args = {"size": size}
        thread = algorithms[algorithm](action="build_matrix", variant=variant, args=args)
    else:
        return JsonResponse({"error": "Unsupported Algorithm: " + algorithm})

    thread.start()
    threadMap[jobId] = thread

    return JsonResponse(request_obj)


# noinspection PyUnusedLocal
def is_matrix_available(request, algorithm, variant, size):
    if algorithm in algorithms:
        current_algorithm = algorithms[algorithm]()
        available = (not current_algorithm.need_matrix()) or os.path.isfile(
            get_matrix_filename(algorithm, variant, size // current_algorithm.ratio))
        return JsonResponse({"matrixAvailable": available})
    else:
        return JsonResponse({"error": "Unsupported Algorithm: " + algorithm})


# noinspection PyUnusedLocal
def reconstruct(request, method, tolerance, filename):
    global jobId
    global algorithms
    jobId += 1
    request_obj = {"requestId": jobId}
    args = filename.split(".")
    if len(args) < 4:
        return JsonResponse({"error": "Filename is not a radon transform"})
    else:
        target_filename = ".".join(args[0:len(args) - 3]) + "." + args[len(args) - 1]
        algorithm = args[len(args) - 3]
        variant = args[len(args) - 2]
        source = "radon_server/static/radon/" + filename[:-3] + "npy"
        target = "radon_server/static/reconstructed/" + target_filename
        original = "radon_server/static/uploaded/" + target_filename
        request_obj["target"] = target_filename

        if algorithm in algorithms:
            args = {"source_file": source, "target_file": target, "original_file": original,
                    "tolerance": math.pow(1E-01, tolerance)}
            thread = algorithms[algorithm](action="reconstruct", variant=variant, method=method, args=args)
        else:
            return JsonResponse({"error": "Unsupported Algorithm: " + algorithm})

    thread.start()
    thread.started = True
    threadMap[jobId] = thread

    return JsonResponse(request_obj)


# noinspection PyUnusedLocal
def get_job_status(request, job_id):
    response = {}

    if job_id in threadMap.keys():
        thread = threadMap[job_id]

        # update running status
        if thread.progress == 0 and not thread.started:
            response['status'] = "not started"
        elif thread.progress == 100:
            if thread.error is not None:
                response['status'] = "failed"
                response['error'] = thread.error.args[0]
            else:
                response['status'] = "completed"
        else:
            thread.took = (time.time() - thread.startTime) * 1000
            response['status'] = "running"

        response['progress'] = thread.progress
        response['took'] = thread.took
        if thread.action == "transform":
            response['targetFile'] = thread.args["target_file"]
            response['cond'] = thread.cond

            # save current result into file
            thread.save()
        elif thread.action == "build_matrix":
            response["matrix_size"] = thread.matrix_size
        elif thread.action == "reconstruct":
            thread.save()
            response["similarity"] = thread.similarity

        # return status response
        return JsonResponse(response)
    else:
        return JsonResponse({"status": "unknown"})
