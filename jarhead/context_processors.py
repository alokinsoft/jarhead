from django.conf import settings as djsettings

def settings(request):
    def n(key):
        return getattr(djsettings, key, None)

    l = getattr(djsettings, 'SETTINGS_EXPOSE', [])

    return  {
        'settings': { k:n(k) for k in l }
    }