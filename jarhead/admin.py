import os
import hashlib  
import random
import time
import django
 
from django import forms
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.conf import settings
from django.db import models
from django.forms import ClearableFileInput
from django.utils.safestring import mark_safe
from django.contrib import admin

try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse

from sorl.thumbnail import get_thumbnail
try:
    from sorl.thumbnail.fields import ImageField
    from sorl.thumbnail.admin.current import AdminImageWidget as BaseWidget
except ImportError:
    from django.forms import ImageField
    from django.contrib.admin.widgets import AdminFileWidget as BaseWidget

from jarhead.cache import FileCache

class PublishControlAdmin(admin.ModelAdmin):
    change_form_template = 'admin/publish_control_change_form.html'

class SingletonModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        """
        Returns True if the given request has permission to add an object.
        Can be overriden by the user in subclasses.
        """
        return False

    def change_view(self, request, object_id, extra_context=None):
        page, status = self.model.objects.get_or_create()
        if(django.VERSION[0] ==1 and django.VERSION[1] < 6):
            result = super(SingletonModelAdmin, self).change_view(request, str(page.id), extra_context)
        else:
            result = super(SingletonModelAdmin, self).change_view(request, str(page.id), '', extra_context)
        if request.POST.has_key('_save'):
            result['Location'] = reverse('admin:index')
        return result


def thumbnail(image_path):
        im = get_thumbnail(image_path, '200x200', quality=99)
        return u'<img style="border: 1px ridge #C0C0C0;" src="%s" alt="%s" />' % (im.url, image_path)

class AdminResubmitBaseWidget(BaseWidget):
    
    def __init__(self, attrs=None, field_type=None):
        super(AdminResubmitBaseWidget, self).__init__()
        self.cache_key = '' 
        self.field_type = field_type

    def value_from_datadict(self, data, files, name):
        upload = super(AdminResubmitBaseWidget, self).value_from_datadict(data, files, name)
        if upload == FILE_INPUT_CONTRADICTION:
            return upload
        
        self.input_name = "%s_cache_key" % name
        self.cache_key = data.get(self.input_name, "")
        
        if files.has_key(name):
            self.cache_key = self.random_key()[:10]
            upload = files[name]
            FileCache().set(self.cache_key, upload)
        elif self.cache_key:
            restored = FileCache().get(self.cache_key, name)
            if restored:
                upload = restored
                files[name] = upload
        return upload
    
    def random_key(self):
        x = "%s%s%s" % (settings.SECRET_KEY, time.time(), random.random())
        random.seed(x)
        return hashlib.md5(str(random.random())).hexdigest()
    
    def output_extra_data(self, value):
        output = ''
        if value and self.cache_key:
            output += ' ' + self.filename_from_value(value)
        if self.cache_key:
            output += forms.HiddenInput().render(self.input_name, self.cache_key, {})
        return output
    
    def filename_from_value(self, value):
        if value: 
            return os.path.split(value.name)[-1]
        
    
class AdminResubmitFileWidget(AdminResubmitBaseWidget):
    template_name = ClearableFileInput.template_name
    
    def render(self, name, value, attrs=None):
        output = ClearableFileInput.render(self, name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class AdminResubmitImageWidget(AdminResubmitBaseWidget):
    
    def render(self, name, value, attrs=None):
        output = super(AdminResubmitImageWidget, self).render(name, value, attrs)
        output += self.output_extra_data(value)
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name=str(value)
            output = unicode(str(output).replace('Change:', ''))
            output += u' <a href="%s" target="_blank">%s</a>' % (image_url, thumbnail(file_name))
        # else:
            # if self.cache_key:
            #     print dir(FileCache().get(self.cache_key, name))
            #     image = str(FileCache().get(self.cache_key, file))
            #     output += u' <a href="#" target="_blank">%s</a>' % (thumbnail(image))
        return mark_safe(output)


class AdminResubmitMixin(object):

    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, ImageField):
            return db_field.formfield(widget=AdminResubmitImageWidget)
        elif isinstance(db_field, models.FileField):
            if db_field.name in ['before_image', 'after_image']:
                return db_field.formfield(widget=AdminResubmitImageWidget)
            else:
                return db_field.formfield(widget=AdminResubmitFileWidget)
        else:
            return super(AdminResubmitMixin, self).formfield_for_dbfield(db_field, **kwargs)

            