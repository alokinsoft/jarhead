import os
import itertools
from django import forms
from PIL import Image, ImageOps
from django.conf import settings
from django.utils._os import safe_join
from django.core.files.storage import get_valid_filename
from django.core.exceptions import SuspiciousOperation

MEDIA_ROOT = settings.MEDIA_ROOT


class ImageUploadForm(forms.Form):
    image = forms.ImageField(required=True)

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

    def handler(self, file):
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