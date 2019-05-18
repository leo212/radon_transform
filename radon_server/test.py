from django.http import HttpResponse

def index(request):
    """View function for home page of site."""
    # Render the HTML template index.html with the data in the context variable
    response = HttpResponse("{\"status\":\"OK\"}")
    return response
