# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext as _


class QueryForm(forms.Form):
    q = forms.CharField(label=_("Query"), required=False,
                        max_length=100,
                        widget=forms.TextInput(attrs={
                            'placeholder': u"%s..." % _("Type your query"),
                        }))

    def q_clean(self):
        q = super(QueryForm, self).q_clean()
        return q.strip()
