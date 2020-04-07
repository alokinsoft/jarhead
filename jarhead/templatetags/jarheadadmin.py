from collections import OrderedDict
from django.conf import settings
from django.template import Library

register = Library()

@register.simple_tag(takes_context=True)
def admin_reorder(context):
    # sort key function - use index of item in order if exists, otherwise item
    sort = lambda order, item: (order.index(item), "") if item in order else (len(order), item)
    if "app_list" in context:
        # sort the app list
        order = OrderedDict(settings.ADMIN_REORDER)
        context["app_list"].sort(key=lambda app: sort(order.keys(), app["name"]))

        for i, app in enumerate(context["app_list"]):
            # sort the model list for each app
            app_name = app["name"]
            model_order = [m for m in order.get(app_name, [])]
            context["app_list"][i]["models"].sort(key=lambda model: sort(model_order, model["name"]))
    return ''
