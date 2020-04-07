from crispy_forms.layout import *


class Richtext(Field):
    pass

class Image(Field):
    pass

class Row(MultiField):
    def __init__(self, *args, **kwargs):
        super(Row, self).__init__('', *args, **kwargs)
        