import django
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.views.generic import TemplateView, FormView
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import BadHeaderError, mail_managers, EmailMessage

try:
    from django.utils import simplejson as json            
except ImportError:
    import json


class BaseMixin(TemplateResponseMixin):
    view_options = dict(show_subnav=False, show_sidemenu=False)

    def get_context_data(self, **kwargs):
        context = super(BaseMixin, self).get_context_data(**kwargs)
        attrs = dir(self)
        for key in [k for k in attrs if k.startswith('menu_')]:
            context[key] = getattr(self, key)

        #populate context options using the mro; works like mootools options
        mro = self.__class__.mro()
        opts = {}
        for klass in reversed(mro):
            if(django.VERSION[0] ==1 and django.VERSION[1] < 6):
                opts.update(getattr(klass, 'options', {}))
            else:
                opts.update(getattr(klass, 'view_options', {}))
        context.update(opts)
        return context


    def redirect(self, url=None, name=None, args=(), kwargs={}):
        """
            call this eg:
            - self.redirect(url='/static/url/')
            - self.redirect(name='urlconf_name')
            - self.redirect(name='urlconf_name', kwargs={'slug':'blah'})
        """
        if name is not None:
            return HttpResponseRedirect(reverse(name, args=args, kwargs=kwargs))
        elif url is not None:
            return HttpResponseRedirect(url)

    def respond_json(self, data):
        if(django.VERSION[0]==1 and django.VERSION[1]<7):
            return HttpResponse(json.dumps(data), mimetype="application/json")
        else:
            return HttpResponse(json.dumps(data), content_type="application/json")



class BaseView(BaseMixin, TemplateView):
    template_name = "jarhead/undefined.html"




class EmailFormView(BaseMixin, FormView):
    template_name = 'contact_form.html'
    # form_class = SomeForm
    form_context_variable = 'form'
    send_manager_mail = True
    manager_mail_subject = 'Manager notification'
    send_submitter_mail = False
    submitter_mail_subject = 'Submitter notification'
    submitter_email_field = 'email'
    show_form_on_success = False
    manager_mail_template_name = 'web/email/manager_email.html'
    submitter_mail_template_name = 'web/email/submitter_email.html'

    post_only = False
    get_redirect = None
    fail_silently = False

    #instance default vars for context
    form_success = False
    form_error = False
    show_form = True

    def get_context_data(self, **kwargs):
        context = super(EmailFormView, self).get_context_data(**kwargs)
        if 'form' in context:
            context[self.form_context_variable] = context.pop('form', None)
        if self.form_success:
            context.update(dict(
                show_form=True if self.show_form_on_success else False,
                show_success=True
            ))
        elif self.form_error:
            context.update(dict(
                show_form=True,
                show_error=True
            ))
        return context

    def form_invalid(self, form):
        self.form_error = True
        if self.request.is_ajax():
            return self.respond_json({
                'status': False
            })
        return self.render_to_response(self.get_context_data(form=form))

    def notify_managers(self, email_data):
        message = render_to_string(self.manager_mail_template_name, email_data)
        mail_managers(self.manager_mail_subject, '', fail_silently=self.fail_silently, connection=None, html_message=message)

    def notify_submitter(self, email_data):
        message = render_to_string(self.submitter_mail_template_name, email_data)
        email = email_data[self.submitter_email_field]
        mail = EmailMessage(subject=self.submitter_mail_subject,
            body=message,
            from_email=settings.SERVER_EMAIL,
            to=[email],
        )
        mail.content_subtype = "html"
        mail.send()

    def form_valid(self, form):
        self.form_success = True
        email_data = {}

        for field_name in form.fields:
            #TODO: make this a dict with the value and label
            email_data[field_name] = form.cleaned_data[field_name]

        if self.send_manager_mail:
            self.notify_managers(email_data)

        if self.send_submitter_mail:
            self.notify_submitter(email_data)

        if self.request.is_ajax():
            return self.respond_json({
                'status': True
            })

        return self.render_to_response(self.get_context_data(form=form))


    def get(self, request, *args, **kwargs):
        if self.post_only:
            return HttpResponseRedirect(reverse(self.get_redirect))
        return super(EmailFormView, self).get(request, *args, **kwargs)
