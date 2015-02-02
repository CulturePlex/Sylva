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
    DIR_CHOICES = (
        ("asc", _("Ascending")),
        ("desc", _("Descending")),
    )
    rows_number = forms.IntegerField(label=_("Show"),
                                     initial=100,
                                     required=True,
                                     widget=forms.NumberInput(
                                         attrs={'class': 'rows_number'}))
    distinct_result = forms.BooleanField(label=_("distinct"),
                                         required=True,
                                         initial=True,
                                         widget=forms.CheckboxInput(
                                             attrs={'class':
                                                    'distinct_result'}))
    show_mode = forms.ChoiceField(label=_("rows"),
                                  choices=SHOW_MODE_CHOICES,
                                  initial=([c[0] for c in
                                           SHOW_MODE_CHOICES]),
                                  required=True,
                                  widget=forms.Select(
                                      attrs={'class': 'show_mode'}))
    select_order_by = forms.ChoiceField(label=_("and sort by"),
                                        choices=ORDER_BY_CHOICES,
                                        initial=([c[0] for c in
                                                 ORDER_BY_CHOICES]),
                                        required=True,
                                        widget=forms.Select(
                                            attrs={'class': 'select_order'}))
    dir_order_by = forms.ChoiceField(label=_("with direction"),
                                     choices=DIR_CHOICES,
                                     required=True,
                                     widget=forms.Select(
                                         attrs={'class': 'select_dir'}))

    def __init__(self, new_choice=None, *args, **kwargs):
        if new_choice:
            self.ORDER_BY_CHOICES += ((new_choice, new_choice),)
            # We add the new choice to the choices of the select_order_by
            select_order_by = self.base_fields.get('select_order_by')
            select_order_by.choices = self.ORDER_BY_CHOICES
        else:
            # We let the choices by default
            self.ORDER_BY_CHOICES = (("default", _("Default")),)
            select_order_by = self.base_fields.get('select_order_by')
            select_order_by.choices = self.ORDER_BY_CHOICES
        super(QueryOptionsForm, self).__init__(*args, **kwargs)

    def add_new_choice(self, new_choice):
        self.ORDER_BY_CHOICES += ((new_choice, new_choice),)
