# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext as _
from django.forms import ModelForm
from operators.models import Query


class QueryForm(forms.Form):
    q = forms.CharField(label=_("Query"), required=False,
                        max_length=100,
                        widget=forms.TextInput(attrs={
                            'placeholder': u"%s..." % _("Type your query"),
                        }))

    def q_clean(self):
        q = super(QueryForm, self).q_clean()
        return q.strip()


class SaveQueryForm(ModelForm):
    results_count = forms.CharField(label=_("Number of results"),
                                    initial=0, widget=forms.HiddenInput(),)
    last_run = forms.DateTimeField(label=_("Last time run"),
                                   initial=0, widget=forms.HiddenInput(),)

    class Meta:
        model = Query
        fields = ['name', 'description', 'query_dict',
                  'query_aliases', 'query_fields']
        widgets = {
            'query_dict': forms.HiddenInput(),
            'query_aliases': forms.HiddenInput(),
            'query_fields': forms.HiddenInput(),
        }
