from django.db.models import fields as mfields
from django.forms import fields as ffields
from django.db.models.fields import files as mfiles
from django.forms.widgets import Widget, Textarea, FileInput


class RichTextField(mfields.TextField):
    def formfield(self, **kwargs):
        f = super(RichTextField, self).formfield(**kwargs)
        f.widget.attrs.update({
            'class': 'richtext'
        })
        return f

class ImageUploadWidget(FileInput):
    def render(self, name, value, attrs=None):
        v = super(ImageUploadWidget, self).render(name, value, attrs)
        print v, type(value), value.url
        return v

class ImageUploadField(ffields.ImageField):
    widget = ImageUploadWidget


class ImageField(mfiles.ImageField):
    def __init__(self, *args, **kwargs):
        self.size_policy = kwargs.pop('size_policy', None)
        return super(ImageField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': ImageUploadField}
        defaults.update(kwargs)
        return super(ImageField, self).formfield(**defaults)
