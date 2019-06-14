"""radon_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import serve
from . import files
from . import transform
from . import upload

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', files.get_status, name='get_status'),
    path('get_filelist/<str:folder>', files.get_filelist),
    path('transform/<str:algorithm>/<str:variant>/<str:filename>', transform.transform),
    path('reconstruct/<str:method>/<int:tolerance>/<str:filename>', transform.reconstruct),
    path('build_matrix/<str:algorithm>/<str:variant>/<int:size>', transform.build_matrix),
    path('is_matrix_available/<str:algorithm>/<str:variant>/<int:size>', transform.is_matrix_available),
    path('get_job_status/<int:job_id>', transform.get_job_status),
    path('upload/', csrf_exempt(upload.upload_file)),
    path('get_image/<str:filename>', serve.get_image),
    path('get_result/<str:filename>', serve.get_result),
    path('get_reconstructed/<str:filename>', serve.get_reconstructed)
]
