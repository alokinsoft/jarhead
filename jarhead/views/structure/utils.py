import re
import copy

## Utility methods for use by stucture.



def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '_', value)

def slugify_klass(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip())
    return re.sub('[-\s]+', '', value)

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and hasattr(el, '__getitem__') and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


