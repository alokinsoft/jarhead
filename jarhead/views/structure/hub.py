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

from .base import space, controller, BaseView, BaseMixin, TemplateView, purl
from .utils import *
from .media import ImageUploadView, ImageUploadForm
from .fields import ImageField as JHImageField

MEDIA_ROOT = settings.MEDIA_ROOT

class URLArgs(object):
    def __init__(self, regex, view, kwargs=None, name=None, prefix=''):
        self.regex = regex
        self.view = view
        self.kwargs = kwargs
        self.name = name
        self.prefix = prefix

    def as_url(self):
        return url(self.regex+'$', self.view, self.kwargs, self.name, self.prefix)

    def as_concrete(self, args=[], kwargs={}):
        return purl.from_string(reverse(self.name, args=args, kwargs=kwargs))



class hub(space):
    '''
    Collection of model editors, simple views, etc collected in a set of blocks
    Each block has a name and a list of controllers.
    The hub has a root view that renders this dashboard
    '''
    template_name = 'hub/home.html'

    def __init__(self, name, blocks=None, options=None, root_view=None, **kwargs):
        self.name = name
        self.home = True #TODO: what if hubs are sub-objects?
        self.nav_label = kwargs.get('nav_label', name)
        self._navigation = None
        self.slug = kwargs.get('slug', slugify(name))
        self.display_klass = kwargs.get('display_klass', str(slugify_klass(self.name)))

        self.blocks = blocks

        self.root_view_options = options

        #setup the root view for the hub
        self.root_view = root_view

        self.hub = self
        self.parent = None


        ## used only during request processing (refreshed for every request)
        self.path_segment = None

    #final stage in initialization
    def freeze(self, parent=None, prefix=None):
        path = copy.copy(prefix) if prefix is not None else []
        path.append(self.slug)
        self.path = path
        self.parent = parent
        for block in self.blocks:
            block.freeze(parent=self, prefix=path)
        return self

    def _root_view_url_pattern(self, parent_fragment=None):
        '''
        returns a valid url object and a regex pattern fragment
        '''
        if self.root_view is None:
            root_view = '{}GeneratedHubRootView'.format(self.display_klass)
            self.root_view = type(root_view, (HubRootView,), self.root_view_options)

        u = ('^' if self.home else '^') + '/'.join(self.path)+'/'
        n = '.'.join(self.path)

        return URLArgs(u, self.root_view.as_view(parent=self, hub=self), name=n, kwargs=dict())

    def urlpatterns(self, parent_fragment=None):
        u = []
        p = self._root_view_url_pattern(parent_fragment)
        u.append(p.as_url())

        for b in self.blocks:
            u.extend(b.urlpatterns(parent_fragment=p.regex))

        return u

    # per request processing
    def clear_request_params(self):
        self.path_segment = None


    def process_request(self, request):
        super(hub, self).process_request(request)
        
    def process_response(self, response):
        super(hub, self).process_response(response)




    def root_navigations(self, request=None):
        '''
        returns items one after another, with some metadata
        each nav_item is guarateed to have a step_type, label and url
        ''' 
        u = purl.from_string('/').add_path_segment(self.slug)
        yield NavItem('root', self.nav_label, url=u)

        for x in self.blocks:
            for n in x.iter_navigations(request, parent_path=u):
                yield n

    def iter_navigations(self, request=None, parent_path=None):
        '''
        returns items one after another, with some metadata
        each nav_item is guarateed to have a step_type, label and url
        ''' 
        u = parent_path.add_path_segment(self.slug)
        yield NavItem('root', self.nav_label, url=u)

        for x in self.blocks:
            for n in x.iter_navigations(request, parent_path=u):
                yield n

    def extract_path_segments(self, path_segments):
        self.path_segment = path_segments.pop(0)

    @property
    def hub(self):
        return self._hub

    @hub.setter
    def hub(self, hub):
        self._hub = hub
        for x in self.blocks:
            x.hub = hub





class block(controller):
    def __init__(self, name, *controllers, **kwargs):
        self.name = name
        self._hub = None
        self.nav_label = kwargs.get('nav_label', name)
        self.slug = kwargs.get('slug', slugify(name))
        self.controllers = controllers
        self.parent = None

    def urlpatterns(self, parent_fragment=None):
        u = []
        p = parent_fragment + self.slug + '/'
        for c in self.controllers:
            u.extend(c.urlpatterns(parent_fragment=p))
        return u

    def freeze(self, parent, prefix=None):
        path = copy.copy(prefix) if prefix is not None else []
        path.append(self.slug)
        self.path = path
        self.parent = parent
        for c in self.controllers:
            c.freeze(parent=self, prefix=path)
        return self

    def clear_request_params(self):
        self.path_segment = None

    def iter_navigations(self, request=None, parent_path=None):
        yield NavItem('enter_submenu', self.nav_label)
        p = parent_path.add_path_segment(self.slug)
        for x in self.controllers:
            for y in x.iter_navigations(request, parent_path=p):
                yield y
        yield NavItem('end_submenu', self.nav_label)

    def extract_path_segments(self, path_segments):
        self.path_segment = path_segments.pop(0)


    def check_permission(self, request, viewkwargs):
        '''
        check if the current user has permissions for this block
        default True
        '''
        return True

    @property
    def hub(self):
        return self._hub

    @hub.setter
    def hub(self, hub):
        self._hub = hub
        for x in self.controllers:
            x.hub = hub



class BaseController(controller):
    pass



class master_detail(BaseController):
    '''
    Controller for a Master Detail UI

    Primarily, there are 2 views:
    - changelist: displays a list of objects per some criteria
    - update_view: allows to edit an existing object
    - create_view allows to customize the add flow
    '''
    def __init__(self, name, model, **kwargs):
        self.name = name
        self.nav_label = kwargs.get('nav_label', name)
        self.slug = kwargs.get('slug', slugify(name))
        self.display_klass = kwargs.get('display_klass', str(slugify_klass(self.name)))
        self._hub = None
        self.model = model
        self.parent = None

        from django.apps import apps
        if isinstance(self.model, basestring):
            self.model = apps.get_model(self.model)

        self.changelist = kwargs.get('changelist', None)
        self.update_view = kwargs.get('update_view', None)
        self.create_view = kwargs.get('create_view', None)

        self.view_options = dict(name=self.name, title=self.name)

        self.changelist_options = dict(template_name='jarhead/generic_changelist.html', model=self.model)
        self.changelist_options.update(kwargs.get('changelist_options', {}))

        self.image_upload_view_options = dict(template_name='jarhead/undefined.html', model=self.model)
        self.image_upload_view_options.update(kwargs.get('image_upload_view_options', {}))

        self.update_view_options = dict(template_name='jarhead/generic_update_view.html', model=self.model)
        self.update_view_options.update(kwargs.get('detail_view_options', {}))
        self.update_view_options.update(kwargs.get('update_view_options', {}))

        self.create_view_options = dict(template_name='jarhead/generic_create_view.html', model=self.model)
        self.create_view_options.update(kwargs.get('detail_view_options', self.update_view_options))
        self.create_view_options.update(kwargs.get('create_view_options', {}))

        self.fk_field_name = kwargs.get('fk_field_name', None)
        self.scoped_object = None

    # @property
    # def nav(self):
    #     return (self.nav_label, self.root_url)


    def _changelist_url_pattern(self, parent_fragment=None):
        basen = '.'.join(self.path)
        u = ('^' if parent_fragment is None else parent_fragment) + self.slug + '/'
        n = '.'.join(self.path) +'.changelist'
        k = dict(parent=self)
        v = self.generate_view('changelist', Changelist, self.changelist_options)
        v = v.as_view(parent=self, hub=self.hub, create_url_name=basen+'.create', update_url_name=basen+'.update')
        return URLArgs(u, v, name=n, kwargs=k)

    def _update_view_url_pattern(self, parent_fragment=None):
        basen = '.'.join(self.path)
        u = ('^' if parent_fragment is None else parent_fragment) + self.slug + r'/(\d+)/'
        n = '.'.join(self.path) + '.update'
        k = dict(parent=self, update=True)
        v = self.generate_view('update_view', UpdateView, self.update_view_options)
        v = v.as_view(parent=self, hub=self.hub, update_url_name=basen+'.update')
        return URLArgs(u, v, name=n, kwargs=k)

    def _create_view_url_pattern(self, parent_fragment=None):
        basen = '.'.join(self.path)
        u = ('^' if parent_fragment is None else parent_fragment) + self.slug + '/create/'
        n = '.'.join(self.path) + '.create'
        k = dict(parent=self, create=True)
        v = self.generate_view('create_view', CreateView, self.create_view_options)
        v = v.as_view(parent=self, hub=self.hub, update_url_name=basen+'.update')
        return URLArgs(u, v, name=n, kwargs=k)

    def _image_upload_view_url_pattern(self, parent_fragment=None):
        basen = '.'.join(self.path)
        u = ('^' if parent_fragment is None else parent_fragment) + self.slug + '/_image_upload/'
        n = '.'.join(self.path) + '.image_upload'
        k = dict(parent=self, create=True)
        v = self.generate_view('image_upload', ImageUploadView, self.image_upload_view_options)
        v = v.as_view(parent=self, hub=self.hub)
        return URLArgs(u, v, name=n, kwargs=k)


    def urlpatterns(self, parent_fragment=None):
        urls = []
        clu = self._changelist_url_pattern(parent_fragment)
        urls.append(clu.as_url())
        uvu = self._update_view_url_pattern(parent_fragment=parent_fragment)
        urls.append(uvu.as_url())
        cvu = self._create_view_url_pattern(parent_fragment=parent_fragment)
        urls.append(cvu.as_url())
        iuv = self._image_upload_view_url_pattern(parent_fragment=parent_fragment)
        urls.append(iuv.as_url())
        return urls

    def freeze(self, parent=None, prefix=None):
        path = copy.copy(prefix) if prefix is not None else []
        path.append(self.slug)
        self.path = path
        self.parent = parent
        return self


    def clear_request_params(self):
        self.path_segment = None
        self.path_segment_id = None
        self.scoped_object = None #mirror the scope object of the parent; if this is a child of a master_hub

    def process_request(self, request):
        if isinstance(request.view, self.update_view):
            request.view.kwargs[request.view.pk_url_kwarg] = self.path_segment_id

        for p in reversed(self.parents()):
            if hasattr(p, 'scope_object'):
                if p.scope_object is not None:
                    self.scoped_object = p.scope_object
                    break


    def process_response(self, request):
        super(master_detail, self).process_response(request)

    def iter_navigations(self, request=None, parent_path=None):
        u = parent_path.add_path_segment(self.slug)
        yield NavItem('item', self.nav_label, url=u)

    def extract_path_segments(self, path_segments):
        self.path_segment = path_segments.pop(0)

        if len(path_segments) > 0:
            self.path_segment_id = path_segments.pop(0)
            if self.path_segment_id == '_image_upload':
                pass

    @property
    def hub(self):
        return self._hub

    @hub.setter
    def hub(self, hub):
        self._hub = hub







class master_hub(BaseController):
    '''
    A Hub that groups multiple editors based on a single object

    sub blocks can contain:
    - master_detail, exposing a set of objects related to the master_hub scope with changelist and create/update views
    - related_formset, exposing a set of objects as a single editor
    '''

    template_name = 'hub/home.html'

    def __init__(self, name, model=None, blocks=None, options=None, root_view=None, **kwargs):
        self.name = name
        self.home = True #TODO: what if hubs are sub-objects?
        self.nav_label = kwargs.get('nav_label', name)
        self._navigation = None
        self.slug = kwargs.get('slug', slugify(name))
        self.display_klass = kwargs.get('display_klass', str(slugify_klass(self.name)))

        self.blocks = blocks if blocks is not None else []

        self._hub = None
        self.model = model

        from django.apps import apps
        if isinstance(self.model, basestring):
            self.model = apps.get_model(self.model)

        self.changelist = kwargs.get('changelist', None)
        self.root_view = kwargs.get('root_view', None)

        self.view_options = dict(name=self.name, title=self.name)

        self.changelist_options = dict(template_name='jarhead/generic_changelist.html', model=self.model, has_create_view=False)
        self.changelist_options.update(kwargs.get('changelist_options', {}))

        self.root_view_options = dict(template_name='jarhead/generic_master_hub_root.html', model=self.model)
        self.root_view_options.update(kwargs.get('root_view_options', {}))

        self.path_segment = None
        self.path_segment_id = None
        self.scope_object = None

    def _changelist_url_pattern(self, parent_fragment=None):
        basen = '.'.join(self.path)
        u = (r'^' if parent_fragment is None else parent_fragment) + self.slug + r'/'
        n = '.'.join(self.path) +'.changelist'
        k = dict(parent=self)
        v = self.generate_view('changelist', Changelist, self.changelist_options)
        v = v.as_view(parent=self, hub=self.hub, outer_hub=self.hub, create_url_name=basen+'.create', update_url_name=basen+'.root')
        return URLArgs(u, v, name=n, kwargs=k)

    def _root_view_url_pattern(self, parent_fragment=None):
        u = (r'^' if parent_fragment is None else parent_fragment) + self.slug + r'/(\d+)/'
        n = '.'.join(self.path) + '.root'
        k = dict(parent=self)
        v = self.generate_view('root_view', MasterHubRootView, self.root_view_options)
        v = v.as_view(parent=self, hub=self, outer_hub=self.hub)
        return URLArgs(u, v, name=n, kwargs=k)

    def urlpatterns(self, parent_fragment=None):
        urls = []
        cu = self._changelist_url_pattern(parent_fragment=parent_fragment)
        urls.append(cu.as_url())
        rup = self._root_view_url_pattern(parent_fragment=parent_fragment)
        urls.append(rup.as_url())
        for b in self.blocks:
            urls.extend(b.urlpatterns(parent_fragment=rup.regex))
        return urls

    def freeze(self, parent=None, prefix=None):
        path = copy.copy(prefix) if prefix is not None else []
        path.append(self.slug)
        self.path = path
        self.parent = parent
        for block in self.blocks:
            block.freeze(self, prefix=path)
        return self

    def clear_request_params(self):
        self.path_segments = None
        self.path_segment_id = None
        self.scope_object = None

    def process_request(self, request):
        if self.path_segment_id is not None:
            self.scope_object = self.model.objects.get(pk=self.path_segment_id)

    def process_response(self, response):
        pass

    def iter_navigations(self, request=None, parent_path=None):
        u = parent_path.add_path_segment(self.slug)
        yield NavItem('item', self.nav_label, url=u)

    def root_navigations(self, request=None):
        '''
        return the root URL for the hub below
        '''
        # yield NavItem('root', self.nav_label, url=self.changelist_url[1])
        u = purl.from_string('/')
        for x in self.parents():
            u = u.add_path_segment(x.path_segment)
        u = u.add_path_segment(self.path_segment).add_path_segment(self.path_segment_id)

        for x in self.blocks:
            for n in x.iter_navigations(request, parent_path=u):
                yield n

    def extract_path_segments(self, path_segments):
        self.path_segment = path_segments.pop(0)

        if len(path_segments) > 0:
            self.path_segment_id = path_segments.pop(0)


    @property
    def hub(self):
        return self._hub

    @hub.setter
    def hub(self, hub):
        self._hub = hub
        for x in self.blocks:
            x.hub = self



class singleton(master_detail):
    '''
    Goes to the only object defined., if there is no defined object, then create one.
    If fk_foreign_key is defined, the singular object is determined by the nearest
    scope object in the parent chain (called scoped_object in the code).

    Hack: If scoped_object is of the same type as self's model, then it is taken as the scope_object for this controller
    '''

    def __init__(self, *args, **kwargs):
        super(singleton, self).__init__(*args, **kwargs)

        self.fk_field_name = kwargs.get('fk_field_name', None)
        self.scoped_object = None
        self.scope_object = None


    def urlpatterns(self, parent_fragment=None):
        urls = []
        up = self._create_view_url_pattern(parent_fragment=parent_fragment)
        urls.append(up.as_url())
        up = self._update_view_url_pattern(parent_fragment=parent_fragment)
        urls.append(up.as_url())
        return urls

    def iter_navigations(self, request=None, parent_path=None):
        self._populate_scope_object(request)
        if self.scope_object is None:
            u = parent_path.add_path_segment(self.slug).add_path_segment('create')
        else:
            u = parent_path.add_path_segment(self.slug).add_path_segment(str(self.scope_object.pk))
        yield NavItem('item', self.nav_label, url=u)


    def clear_request_params(self):
        self.path_segments = None
        self.path_segment_id = None
        self.scoped_object = None
        self.scope_object = None

    def _populate_scope_object(self, request):
        try:
            for p in reversed(self.parents()):
                if hasattr(p, 'scope_object'):
                    if p.scope_object is not None:
                        self.scoped_object = p.scope_object
                        break
            if self.fk_field_name is not None:
                self.scope_object = self.model.objects.get(**{
                    self.fk_field_name: self.scoped_object
                })
            else:
                if isinstance(self.scoped_object, self.model):
                    #edit one or more fields of the parent object
                    self.scope_object = self.scoped_object
                else:
                    self.scope_object = self.model.objects.get()
        except self.model.DoesNotExist as e:
            self.scope_object = None

    def process_request(self, request):
        if self.path_segment_id == 'create':
            return
        self._populate_scope_object(request)
        if self.scope_object is not None:
            if isinstance(request.view, self.update_view):
                request.view.kwargs[request.view.pk_url_kwarg] = self.path_segment_id

# Cusom Views

class HubRootView(BaseView):
    '''
    Renders the blocks in the dashboard
    '''
    def get_context_data(self, **kwargs):
        context = super(HubRootView, self).get_context_data(**kwargs)
        if self.request.method == 'GET':
            context.update({
                'blocks': [block for block in self.hub.blocks if block.check_permission(self.request, self.kwargs)],
            })
        return context


class MasterHubRootView(HubRootView):
    '''
    Renders the blocks in the dashboard
    '''
    outer_hub = None #the outer hub view


class NavItem(object):
    '''
    This class holds the data generated with iter_navigations()
    step_type can be: root, start_submenu, end_submenu, item, button
    '''
    def __init__(self, step_type, label, url=None, **kwargs):
        self.step_type = step_type
        self.label = label
        self.url = url
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '<nav type="{}" label="{}">'.format(self.step_type, self.label)

class ChangelistItem(object):
    '''
    This is the model for the changelist view; essentially a list of ChangelistItem objects for now. The template takes a list of such objects to render them.
    '''
    def __init__(self, cl, item):
        self.cl = cl
        self.item = item

    def update_url(self):
        u = self.cl.update_url_name
        pk = self.item.pk

        args = self.cl.get_path_segment_ids()
        return reverse(self.cl.update_url_name, args=args+[self.item.pk])

    def __getattr__(self, attr):
        if attr.startswith('field_') or attr.startswith('mediabox_'):
            attr = getattr(self.cl, attr, None)
            if callable(attr):
                return attr(self)
            else:
                return attr
        else:
            raise AttributeError


class Changelist(BaseView):
    create_url_name = None
    update_url_name = None
    has_create_view = True
    items_per_page = 25
    item_class = ChangelistItem
    list_style = 'tabular'
    fields = None


    def get_template_names(self):
        return [self.template_name]


    def get_fields(self):
        if self.fields is not None:
            return self.fields
        else:
            return ['id']


    def field_labels(self):
        return [f.verbose_name for f in self.model._meta.get_fields() if f.name in self.get_fields()]

    def field_values(self, cli):
        '''
            cli = ChangelistItem
        '''
        return [getattr(cli.item, field, '') for field in self.get_fields()]


    def mediabox_title(self, cli):
        return getattr(cli.item, self.mediabox['title'], '')

    def mediabox_description(self, cli):
        return getattr(cli.item, self.mediabox['description'], '')


    def get_context_data(self, **kwargs):
        context = super(Changelist, self).get_context_data(**kwargs)
        self.inject_paginator(context)
        return context

    def get_create_url(self):
        args = self.get_path_segment_ids()
        return reverse(self.create_url_name, args=args)

    def inject_paginator(self, context):
        ol = self.object_list
        paginator = Paginator(ol, 25)

        pagen = self.kwargs.get('page', 1)
        try:
            page = paginator.page(pagen)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page = paginator.page(paginator.num_pages)

        context.update({
            'page': page,
            'page_items': [self.item_class(self, item) for item in page],
            'paginator': paginator,
            'object_list': ol
        })

    @property
    def object_list(self):
        if hasattr(self.parent, 'fk_field_name') and self.parent.fk_field_name is not None:
            filters = {
                self.parent.fk_field_name: self.parent.scoped_object
            }
            return self.model.objects.filter(**filters)
        return self.model.objects.all()


class UpdateForm(model_forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(crispy.Submit('submit', 'Submit'))


class FormGeneratorMixin(object):
    def get_form(self, form_class=None):
        """
        Returns an instance of the form to be used in this view.
        """
        if form_class is None:
            form_class = self.get_form_class()
        fc = form_class(**self.get_form_kwargs())
        # fc.helper.form_action = self.get_update_url()

        layout = self.parent.create_view_options.get('layout', None)
        if layout is not None:
            fc.helper.layout = layout
        return fc


    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        fields = self.fields if self.fields is not None else '__all__'
        exclude = getattr(self, 'exclude', None)
        return model_forms.modelform_factory(
            model=self.model, 
            form=UpdateForm, 
            fields=fields, 
            exclude=exclude,
            formfield_callback=self.get_formfield, 
            widgets=None, 
            localized_fields=None,
            labels=None, 
            help_texts=None, 
            error_messages=None
        )

    def get_formfield(self, model_field):
        return model_field.formfield()


class UpdateView(BaseMixin, FormGeneratorMixin, BaseUpdateView):
    update_url_name = None

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)

        #updating
        context['image_upload_form'] = ImageUploadForm()
        return context

    def get_object(self):
        return self.model.objects.get(pk=self.parent.path_segment_id)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(UpdateView, self).get(request, *args, **kwargs)

    def get_update_url(self):
        args = self.get_path_segment_ids()
        return reverse(self.update_url_name, args=args)

    def get_success_url(self):
        return self.get_update_url()

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save()
        print "form valid", self.object
        return super(UpdateView, self).form_valid(form)

    def form_invalid(self, form):
        """
        If the form is valid, save the associated model.
        """
        print "form invalid", form.errors
        return super(UpdateView, self).form_invalid(form)

class CreateView(BaseMixin, FormGeneratorMixin, BaseCreateView):
    update_url_name = None

    def get_object(self):
        pass

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        if self.parent.fk_field_name:
            self.object = form.save(commit=False)
            setattr(self.object, self.parent.fk_field_name, self.parent.scoped_object)
            self.object.save()
            form.save_m2m()
        else:
            self.object = form.save()
        return super(CreateView, self).form_valid(form)

    def get_update_url(self):
        args = self.get_path_segment_ids()
        return reverse(self.update_url_name, args=args[:-1]+[self.object.pk])

    def get_success_url(self):
        return self.get_update_url()





# class Blah(object):
#     def __init__(self, *args, **kwargs):
#         pass

# globals().update({n: type(str(n), (Blah,), {}) for n in """
# basic_view
# changelist
# detail_view
# employee_detail
# owner_detail
# profiles
# market_pro_view
# Facility
# Employee
# User
# model_group
# Users
# Groups
# Permissions
# simple_list
# FacilityImage
# FacilityReviews
# """.split('\n')})

