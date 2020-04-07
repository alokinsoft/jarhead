from __future__ import unicode_literals

import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from classytags.arguments import Argument
from classytags.core import Tag, Options

register = template.Library()


@register.tag
class Attr(Tag):
    name = 'attr'
    options = Options(
        Argument('name', resolve=True),
        Argument('var', required=False, resolve=True)
    )

    def render_tag(self, context, name, var, **kwargs):
        output = ''
        var = context.get('var', var)
        if var is not None:
            output = '{name}="{var}"'.format(name=name, var=var)
        return output


class SafeJSONEncoder(DjangoJSONEncoder):
    def _recursive_escape(self, o, esc=conditional_escape):
        if isinstance(o, dict):
            return type(o)((esc(k), self._recursive_escape(v)) for (k, v) in o.iteritems())
        if isinstance(o, (list, tuple)):
            return type(o)(self._recursive_escape(v) for v in o)
        try:
            return type(o)(esc(o))
        except ValueError:
            return esc(o)

    def encode(self, o):
        value = self._recursive_escape(o)
        return super(SafeJSONEncoder, self).encode(value)

@register.filter('json')
def json_filter(value):
    """
    Returns the JSON representation of ``value`` in a safe manner.
    """
    return mark_safe(json.dumps(value, cls=SafeJSONEncoder))
