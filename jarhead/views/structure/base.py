from abc import ABCMeta as abc, abstractmethod, abstractproperty

from ..base import BaseView as JHBaseView, BaseMixin as JHBaseMixin, TemplateView

from django.utils.decorators import method_decorator



import copy, itertools, json, os, re
from pprint import pprint

from PIL import Image, ImageOps
from purl import URL as PURL

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



class purl(PURL):
    # def add_path_segment(self, arg):
    #     if arg.endswith(u'/'):
    #         arg = arg + u'/'
    #     return super(purl, self).add_path_segment(arg)

    def path(self, value=None):
        if value is not None:
            if value[-1] != '/':
                value = value+'/'
        return super(purl, self).path(value=value)

class controller(object):
    __metaclass__ = abc

    @abstractmethod
    def urlpatterns(self, parent_fragment=None):
        pass

    @abstractmethod
    def freeze(self, parent=None, prefix=None):
        pass

    def clear_request_params(self):
        '''
        completely clear all the request params from the earlier request
        '''
    def extract_path_segments(self, path_segments):
        '''
        extract segments from the current path
        allows us to fill the dyanamic navigation
        '''
    def process_request(self, request):
        '''
        pre-process the request before dispatch
        '''
    def process_response(self, response):
        '''
        pre-process the response before returning the response
        '''

    def generate_view(self, attribute, base_klass, base_klass_options):
        parent_klass = getattr(self, attribute, None)
        if parent_klass is None:
            parent_klass = base_klass 
        elif 'Generated' in parent_klass.__name__:
            return parent_klass
        name = '{}Generated{}'.format(self.display_klass, base_klass.__name__)
        setattr(self, attribute, type(name, (parent_klass,), base_klass_options))
        return getattr(self, attribute)

    def parents(self):
        '''
        returns a list of parents
        '''
        parents = []
        p = self.parent
        while p is not None:
            parents.insert(0, p)
            p = p.parent
        return parents

    # @abstractproperty
    # def nav(self):
    #     pass

class space(controller):

    @abstractmethod
    def root_navigations(self, request=None):
        pass


class BaseMixin(JHBaseMixin):
    hub = None
    outer_hub = None #1 level of nesting
    parent = None

    def get_context_data(self, **kwargs):
        #put navigations into the context
        context = super(BaseMixin, self).get_context_data(**kwargs)
        context.update({
            'hub': self.hub,
            #'navigation': self.hub.iter_navigations(self.request)
        })
        return context

    def parents(self):
        return self.parent.parents() + [self.parent]

    def get_path_segment_ids(self):
        args = []
        for p in self.parents():
            v = getattr(p, 'path_segment_id', None)
            if v is not None:
                args.append(v)
        return args

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        request.view = self
        request.purl = purl(request.path)

        path_segments = list(request.purl.path_segments())

        request.parents = self.parents()

        # print "All parents"
        # pprint(request.parents)

        for p in request.parents:
            p.clear_request_params()

        #resolve dynamic navigations
        for p in request.parents:
            p.extract_path_segments(path_segments)

        
        [getattr(p, 'process_request', lambda request: None)(request) for p in request.parents]
        response = super(BaseMixin, self).dispatch(request, *args, **kwargs)
        [getattr(p, 'process_response', lambda request: None)(request) for p in request.parents]
        return response


class BaseView(BaseMixin, TemplateView):
    template_name = "jarhead/undefined.html"
