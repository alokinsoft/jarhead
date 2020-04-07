import re
import copy


from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import RedirectView

from ..base import BaseView
from .pages import *

class navigation(object):
    """
        Collects a set of spaces and configures them for use by the url resolver
        organizes views into spaces and allows prefixing URLs
    """
    def __init__(self, view_modules=None, templates_root=None, *args, **kwargs):
        self.all = kwargs
        self.view_modules = view_modules
        self.templates_root = templates_root

    def search_views(self, name):
        for m in self.view_modules:
            if hasattr(m, name):
                return getattr(m, name)

    def freeze(self):
        # print navigation.all
        ## pass on the central navigation class (to avoid singletons)s
        for nav in self.all.values():
            print nav
            nav.navigation = self
            nav.freeze()
        return self

    def urlpatterns(self):
        """
            collects the urlpatterns from the configured pages below it

            this is used to inject url-patterns from the spaces below it
        """
        return flatten([nav.urlpatterns() for nav in self.all.values()])

    def search(self, nav_id=None):
        for nav in self.all.values():
            n = nav.search(nav_id=nav_id)
            if n is not None:
                return n
        return None


