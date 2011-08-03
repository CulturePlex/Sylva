# -*- coding: utf-8 -*-
from django import forms
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.utils.translation import gettext as _

from data.models import Data
from graphs.models import Graph
from engines.models import Instance


class GraphForm(ModelForm):
    instance = forms.ModelChoiceField(queryset=Instance.objects.none(),
                                      empty_label=_("No instances available"),
                                      required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(GraphForm, self).__init__(*args, **kwargs)
        if user:
            instances = Instance.objects.filter(owner=user)
            self.fields["instance"].queryset = instances
            empty_label = _("Choose your backend instance")
        self.fields["instance"].empty_label = empty_label
        help_text = _("Buy a <a href='%s'>new instance</a>.") \
                    % reverse("dashboard")
        self.fields["instance"].help_text = help_text

    class Meta:
        model = Graph
        fields = ("name", "description")
