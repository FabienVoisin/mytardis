from django.utils.safestring import mark_safe
from django.forms.util import flatatt
from django.forms.widgets import TextInput, Widget


class DelimitedInput(TextInput):
    """
        An extended TextInput widget for typing in a list of strings with delimter
        The default delimter is comma
    """
    def __init__(self, attrs=None):
        if attrs is not None:
            self.delimiter = attrs.pop('delimiter', ',')
        super(DelimitedInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if isinstance(value, list):
            value = ("%s " % self.delimiter).join(value)
        return super(DelimitedInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        value = super(DelimitedInput, self).value_from_datadict(data,
                                                                     files,
                                                                     name)
        return [v.strip(' ') for v in value.split(self.delimiter)]


class Label(Widget):
    tag = "label"

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<%(tag)s%(attrs)s>%(value)s</%(tag)s>' %
                         {'attrs': flatatt(final_attrs),
                          'value': value,
                          'tag': self.tag})


class Span(Label):
    tag = "span"
