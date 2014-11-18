# -*- coding: utf-8 -*-
from datetime import datetime
from django import forms
from django.utils.translation import gettext as _
from django.forms import ModelForm
from queries.models import Query


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
                                   initial=datetime.now(),
                                   widget=forms.HiddenInput(),)

    class Meta:
        model = Query
        fields = ['name', 'description', 'query_dict',
                  'query_aliases', 'query_fields']
        widgets = {
            'query_dict': forms.HiddenInput(),
            'query_aliases': forms.HiddenInput(),
            'query_fields': forms.HiddenInput(),
        }


class QueryDeleteConfirmForm(forms.Form):
    CHOICES = (
        (1, _("Yes")),
        (0, _("No")),
    )
    confirm = forms.ChoiceField(label=_("Are you sure you want to delete "
                                        "this? All related reports "
                                        "will be removed"),
                                choices=CHOICES, required=True,
                                widget=forms.RadioSelect())


class QueryOptionsForm(forms.Form):
    SHOW_MODE_CHOICES = (
        ("per_page", _("Per page")),
        ("in_total", _("In total")),
    )
    ORDER_BY_CHOICES = (
        ("default", _("Default")),
    )
    rows_number = forms.IntegerField(label=_("Show"),
                                     initial=100,
                                     required=True,
                                     widget=forms.NumberInput(
                                         attrs={'class': 'rows_number'}))
    show_mode = forms.ChoiceField(label=_("rows"),
                                  choices=SHOW_MODE_CHOICES,
                                  initial=([c[0] for c in
                                           SHOW_MODE_CHOICES]),
                                  required=True,
                                  widget=forms.Select(
                                      attrs={'class': 'show_mode'}))
