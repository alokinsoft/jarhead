
import copy, itertools, json, os, re
from pprint import pprint

from PIL import Image, ImageOps

from django import forms
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.files.storage import get_valid_filename
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db import models
from django.forms import fields as form_fields
from django.forms import models as model_forms
from django.http import HttpResponse
from django.utils._os import safe_join
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from django.views.generic.edit import BaseCreateView, BaseUpdateView

from crispy_forms.helper import FormHelper
from crispy_forms import layout as crispy

from .base import BaseView
from .base import space, controller
from .utils import *


class ImageUploadForm(forms.Form):
    image = forms.ImageField(required=True)
    for_field = form_fields.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        # self.helper.form_action = '/dashboard/content/about/_image_upload/'
        self.helper.add_input(crispy.Submit('submit', 'Submit'))


    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        # If the filename already exists, add an underscore and a number (before
        # the file extension, if one exists) to the filename until the generated
        # filename doesn't exist.
        count = itertools.count(1)
        while self.exists(name):
            # file_ext includes the dot.
            name = os.path.join(dir_name, "%s_%s%s" % (file_root, next(count), file_ext))
        return name

    def exists(self, name):
        return os.path.exists(self.path(name))

    def path(self, name):
        location = os.path.join(MEDIA_ROOT, 'image_uploads')
        try:
            path = safe_join(location, name)
        except ValueError:
            raise SuspiciousOperation("Attempted access to '%s' denied." % name)
        return os.path.normpath(path)

    def save(self, file):
        thumbnail_size = (105, 105)
        path = os.path.join(MEDIA_ROOT, 'image_uploads')
        thumbnail_path = os.path.join(path, 'thumbnails')
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(thumbnail_path):
            os.mkdir(thumbnail_path)
        file_name = get_valid_filename(file.name)
        filepath = os.path.join(path, file_name)
        filepath = self.get_available_name(filepath)
        file_name = os.path.basename(filepath)
        destination = open(filepath, 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
        try:
            im = Image.open(filepath)
            thumb = ImageOps.fit(im, thumbnail_size, Image.ANTIALIAS)
            thumb.save(os.path.join(thumbnail_path, "thumbnail_" + file_name), "PNG")
        except:
            pass

class ImageUploadView(BaseView):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ImageUploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(request.FILES['image'])
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



class FileBrowserView(BaseView):
    '''
    Must provide a RESTful service, with HTML template support for managing files for a given context.

    The context can be an existing Model instance, or a Model instance being created

    Options to be provided:
    - per instance storage
    - shared storage for a set of instances, or all instances
    - enhanced support for images
    - previews
    - file metadata

    GET methods require a path. '/' always refers to storage corrsponding to the storage settings
    Content types include: JSON based output, simple HTML templates for file mnaagers

    PUT methods for uploading new files into a folder or creating folders

    POST to create and modify a directory/file


    GET /path/to/directory/

    response: 
    {   
        'name': 'directory',
        'parent': '/path/to/', // If this is /, then parent will be null
        'thumbnail': 'url/to/thumbnail',
        'directories': [
            '/path/to/directory/subdirectory/',
            '/path/to/directory/subdirectory1/'
        ],

        'files': [
            '/path/to/directory/file.ext',
            '/path/to/directory/file2.ext2',
        ]
    }

    '''


