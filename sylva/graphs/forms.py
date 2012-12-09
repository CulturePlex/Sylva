# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import ModelForm, widgets
from django.utils.translation import gettext as _

from graphs.models import Graph
from engines.models import Instance


class GraphForm(ModelForm):
    instance = forms.ModelChoiceField(queryset=Instance.objects.none(),
                                      empty_label=_("No instances available"),
                                      required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(GraphForm, self).__init__(*args, **kwargs)
        graph = self.instance
        queryset = []
        initial = ''
        if graph.pk:
            pk = graph.owner.pk
            queryset = User.objects.filter(pk=pk)
            initial = pk
        elif user:
            pk = user.pk
            queryset = User.objects.filter(pk=pk)
            initial = pk
        self.fields["owner"] = forms.ModelChoiceField(
            queryset=queryset,
            initial=initial,
            widget=forms.HiddenInput())
        if settings.OPTIONS["ENABLE_INSTANCES"]:
            if user:
                instances = Instance.objects.filter(owner=user)
                self.fields["instance"].queryset = instances
                empty_label = _("Choose your backend instance")
                self.fields["instance"].empty_label = empty_label
            help_text = _("Buy a <a href='%s'>new instance</a>.") \
                % reverse("dashboard")
            self.fields["instance"].help_text = help_text
        else:
            self.fields["instance"].widget = forms.HiddenInput()

    class Meta:
        model = Graph
        fields = ("owner", "name", "description", "public")  # Removed relaxed


class GraphDeleteConfirmForm(forms.Form):
    CHOICES = (
        (1, _("Yes")),
        (0, _("No")),
    )
    confirm = forms.ChoiceField(label=_("This operation can't be undone. Are "
                                        "you sure you want to delete this "
                                        "whole graph?"),
                                help_text=_("This can take a few minutes"),
                                choices=CHOICES, required=True,
                                widget=forms.RadioSelect())


class GraphCloneForm(GraphForm):
    CHOICES = (
        ("schema", _("Schema")),
        ("data", _("Data")),
    )
    options = forms.MultipleChoiceField(required=False,
                                        widget=widgets.CheckboxSelectMultiple,
                                        choices=CHOICES,
                                        initial=[c[0] for c in CHOICES],
                                        label=_("Which parts of the graph "
                                                "would you like to clone?"),
                                        help_text=_("Note that your files will"
                                                    " not be copied"))

    class Meta(GraphForm.Meta):
        exclude = ("name", "description", "relaxed", "public",)


class AddCollaboratorForm(forms.Form):
    new_collaborator = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={'class': 'chzn-select',
                                   'data-placeholder': _("Type the name")}),
        empty_label=_(u"Type the name or e-mail")
    )

    def __init__(self, *args, **kwargs):
        self.graph = kwargs.pop("graph", None)
        new_collaborator = kwargs.get("data", {}).get("new_collaborator", None)
        super(AddCollaboratorForm, self).__init__(*args, **kwargs)
        if self.graph and new_collaborator:
            users = User.objects.filter(id=new_collaborator)
            self.fields["new_collaborator"].queryset = users

    def clean_new_collaborator(self):
        new_collaborator = self.cleaned_data["new_collaborator"]
        collabs = self.graph.get_collaborators(include_anonymous=True,
                                               as_queryset=True)
        if (new_collaborator in collabs
                and new_collaborator not in User.objects.all()):
            raise forms.ValidationError((u"Plase, choose a valid user"))
        else:
            return new_collaborator
