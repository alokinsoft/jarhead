from __future__ import unicode_literals
import re
import copy

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import RedirectView

from ..base import BaseView
from .base import space, controller
from .utils import *


class pages(space):
    """
    A space class which describes the layout of a space with Pages in it
    """
    def __init__(self, *args, **kwargs):
        self.all = []
        for x in args:
            if isinstance(x, basestring):
                self.all.append(Page(x))
            else:
                self.all.append(x)
        self._navigation = None
        self.prefix = None

    def __str__(self):
        return '<Pages prefix=%s />'%(self.prefix)

    def freeze(self, prefix=None):
        self.prefix = copy.copy(prefix) if prefix is not None else []
        for page in self.all:
            page.freeze(prefix=prefix)

    def urlpatterns(self):
        return flatten([page.urlpatterns() for page in self.all])

    @property
    def navigation(self):
        return self._navigation

    @navigation.setter
    def navigation(self, navigation):
        self._navigation = navigation
        for x in self.all:
            x.navigation = navigation

    def search(self, nav_id=None):
        for page in self.all:
            n = page.search(nav_id)
            if n is not None:
                return n
        return None

    def find_non_placeholder(self, throw=False):
        for page in self.all:
            p = page.find_non_placeholder(throw=throw)
            if p is not None:
                return p

    # def process_request(self, request):
    #     pass

    # def process_response(self, response):
    #     pass

    # def dispatch(self, request, *args, **kwargs):
    #     pass



class Page(controller):
    name = 'Home'
    nav_label = 'Home'
    title = 'Home Page'
    slug = 'home'
    placeholder = False
    nav_id = None
    home = False

    def __str__(self):
        return '<Page name=%s slug=%s />'%(self.name, self.slug)

    def __init__(self, name, children=None, secondary=None, *args, **kwargs):
        self.name = name
        self.nav_label = kwargs.get('nav_label', name)
        self.slug = kwargs.get('slug', slugify(name))
        self.title = kwargs.get('title', name)
        self.nav_id = kwargs.get('nav_id', None)
        self.home = kwargs.get('home', False)
        self.placeholder = kwargs.get('placeholder', False)
        self.children = children
        self.secondary = secondary
        self.view = kwargs.get('view', slugify_klass(self.name))
        self.display_klass = kwargs.get('display_klass', str(slugify_klass(self.name)))
        self._navigation = None
        self.path = None

    def freeze(self, prefix=None):
        path = copy.copy(prefix) if prefix is not None else []
        path.append(self.slug)
        self.path = path
        if self.children:
            self.children.freeze(prefix=path)
        if self.secondary:
            self.secondary.freeze(prefix=path)

        # if isinstance(self.view, type):
        #   self.navigation.search_views

    def url(self):
        return '/'.join(self.path)

    def urlpatterns(self):
        """
            Generate url patterns for self as well as children and secondary items
        """
        u = '^$' if self.home else '^'+'/'.join(self.path)+'/$'
        n = '.'.join(self.path)

        v = self.view

        ## Check if self is a placeholder, and return a redirect view

        if self.placeholder:
            v = self.find_non_placeholder()
            v = type('%sRedirectedView'%self.display_klass, (RedirectView,), {
                'url': v.url()
            })
            v = v.as_view()


        ## if it's callable, we have the view
        ## if it's a string, we resolve it by name from the views modules list
        ## otherwise, we just generate a template view and return that

        if callable(v):
            v = v #we have a view
        elif isinstance(self.view, basestring):
            #if we just have a string
            v = self.navigation.search_views(self.view)
            if v is None:
                template = ''
                if self.navigation.templates_root:
                    template = self.navigation.templates_root + '/'
                template += '/'.join(self.path)+'.html'
                v = type('%sGeneratedView'%self.display_klass, (BaseView,), {
                    'template_name': template
                })
            v = v.as_view()

        print "url", u, v, n

        l = [url(u, v, name=n)]
        if self.children:
            l.extend(self.children.urlpatterns())
        if self.secondary:
            l.extend(self.secondary.urlpatterns())
        return l

    def find_non_placeholder(self, throw=True):
        if not self.placeholder:
            return self
        if self.children:
            p = self.children.find_non_placeholder(throw=False)
            if p is not None:
                return p
        if self.secondary:
            p = self.secondary.find_non_placeholder(throw=False)
            if p is not None:
                return p

        if throw:
            raise ImproperlyConfigured("No non-placeholder sub page could be found for page: %s"%self)

    def search(self, nav_id=None):
        if self.nav_id == nav_id:
            return self
        elif self.children:
            n = self.children.search(nav_id=nav_id)
            if n is not None:
                return n
        return None

    @property
    def navigation(self):
        return self._navigation

    @navigation.setter
    def navigation(self, navigation):
        self._navigation = navigation
        if self.children:
            self.children.navigation = navigation
        if self.secondary:
            self.secondary.navigation = navigation


    # def process_request(self, request):
    #     pass

    # def process_response(self, response):
    #     pass

    # def dispatch(self, request, *args, **kwargs):
    #     pass
