# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext as _


class SearchForm(forms.Form):
    q = forms.CharField(label=_("Search"), required=False,
                        max_length=100,
                        widget=forms.TextInput(attrs={
                            'placeholder': u"%s..." % _("Search"),
                            'class': 'searchBox',
                        }))

    analytics = forms.BooleanField(required=False,
                                widget=forms.HiddenInput())

    def q_clean(self):
        q = super(SearchForm, self).q_clean()
        return q.strip()
