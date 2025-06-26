from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.http.multipartparser import MultiPartParser


def extract_data_and_files(request):
    if request.META.get('CONTENT_TYPE', '').startswith('multipart/form-data'):
        request.upload_handlers = [TemporaryFileUploadHandler(request)]
        parser = MultiPartParser(request.META, request, request.upload_handlers)
        data, files = parser.parse()
    else:
        data = request.POST
        files = request.FILES
    return data, files
