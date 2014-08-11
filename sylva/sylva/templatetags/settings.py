# -*- coding: utf-8 -*-
from django import template
from django.templatetags.static import PrefixNode

register = template.Library()


class SettingNode(PrefixNode):

    @classmethod
    def handle_token(cls, parser, token, name):
        """
        Class method to parse setting node and return a Node.
        """
        tokens = token.contents.split()
        if len(tokens) > 1 and tokens[2] != 'as':
            raise template.TemplateSyntaxError(
                "Second argument in '%s' must be 'as'" % tokens[0])
        if len(tokens) > 1:
            varname = tokens[3]
        else:
            varname = None
        return cls(varname, name)

    @classmethod
    def handle_simple(cls, name):
        try:
            from django.conf import settings
        except ImportError:
            prefix = ''
        else:
            prefix = getattr(settings, name, '')
        return prefix


@register.tag
def get_setting(parser, token):
    """
    Populates a template variable with a settings variable.

    Usage::

        {% get_setting SETTING [as varname] %}

    Examples::

        {% get_setting INSTALLED_APPS %}
        {% get_setting INSTALLED_APPS as INSTALLED_APPS %}

    """
    var = token.split_contents()[1]
    return SettingNode.handle_token(parser, token, var)
