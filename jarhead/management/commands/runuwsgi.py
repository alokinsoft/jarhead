import django
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys

class Command(BaseCommand):
    help = "Runs the uWSGI server. Configuration is taken from conf/uwsgi.conf"

    def handle(self, *args, **options):
        # exec the uwsgi binary

        uwsgi_config = getattr(settings, 'UWSGI_CONF', 'uwsgi.conf')
        os.environ['UWSGI_XML'] = 'conf/%s'%uwsgi_config
        # if running locally load dev conf file
        if getattr(settings, 'UWSGI_DEV_MODE', False):
            os.environ['UWSGI_XML'] = 'conf/uwsgi_dev.conf'

        arglist = [['uwsgi']]

        venv = os.environ.get('VIRTUAL_ENV', None)

        if venv is None:
            venv = settings.VIRTUAL_ENV



        os.environ['PATH'] = os.environ.get('PATH', '') + ':' + os.path.join(venv, 'bin')
        os.environ['UWSGI_XML'] = os.path.join(venv, getattr(settings, 'PROJECT_DIRNAME', venv), os.environ['UWSGI_XML'])

        #populate a list of useful placeholder vars
        arglist.append(['--set', 'BASEPATH=%s'%venv])
        arglist.append(['--set', 'PROJECTDIR=%s'%getattr(settings, 'PROJECT_DIRNAME', venv)])
        arglist.append(['--set', 'VIRTUAL_ENV=%s'%venv])
        foo, name = os.path.split(venv)
        arglist.append(['--set', 'VIRTUAL_ENV_NAME=%s'%name])

        #map the django admin static assets
        if hasattr(settings, 'ADMIN_MEDIA_PREFIX'):
            paths = [os.path.join(django.__path__[0], 'contrib', 'admin', 'media' ), os.path.join(django.__path__[0], 'contrib', 'admin', 'static', 'admin' )]

            p = None
            for x in paths:
                if os.path.exists(x):
                    p = x
                    break
            if p is not None:
                arglist.append(['--static-map', '%s=%s' % (settings.ADMIN_MEDIA_PREFIX, p)])
            else:
                print ('*** Could not determine admin media!')

        #get uwsgi server name
        uwsgi_server = getattr(settings, 'UWSGI_SERVER', '')

        #set a useful procname for linux -> homedir/venvname
        s = venv.split('/')
        proc_prefix = '%s/%s/%s '%(s[2], s[-1], uwsgi_server) #extra space at the end
        arglist.append(['--procname-prefix', proc_prefix])

        args = []
        [args.extend(x) for x in arglist]

        print (args)

        os.execvp('uwsgi', args)

    def usage(self, subcomand):
        return r"""run this project on the uWSGI server"""
