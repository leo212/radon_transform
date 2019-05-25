from django.views.static import serve as static_serve


def get_image(request, filename):
    """
    serve a single uploaded image
    """
    response = static_serve(request, filename, document_root="radon_server/static/uploaded", show_indexes=False)

    response['Access-Control-Allow-Origin'] = "*"
    return response