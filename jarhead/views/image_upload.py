import os,json
from PIL import Image
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from jarhead.views.base import BaseView
from jarhead.forms import ImageUploadForm


MEDIA_ROOT = settings.MEDIA_ROOT

class ImageUploadView(BaseView):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ImageUploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.handler(request.FILES['image'])
            return HttpResponse("ok")
        else:
            return HttpResponse("error")

class ImageDisplayView(BaseView):
    def get(self, request, *args, **kwargs):
        folder = "image_uploads"
        path = os.path.join(MEDIA_ROOT,folder)
        if os.path.exists(path):
            data = {}
            files = []
            data['path'] = os.path.join('/media',folder)
            data['thumbnail_path'] = os.path.join(data['path'],'thumbnails')
            for f in os.listdir(path):
                file_path = os.path.join(path,f)
                if not f.startswith('.') and os.path.isfile(file_path):
                    d = {}
                    d['name'] = f
                    d['width'] = ""
                    d['height'] = ""
                    try:
                        width, height = Image.open(file_path).size
                        d['width'] = width
                        d['height'] = height
                    except:
                        pass
                    files.append(d)
            data['files']=files
            return HttpResponse(json.dumps(data))
        return HttpResponse(json.dumps({}))
