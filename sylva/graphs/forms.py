# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.utils.translation import gettext as _

from django.conf import settings

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
        if settings.OPTIONS["ALLOWS_INSTANCES"]:
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
        fields = ("name", "description", "relaxed", "public")


class GraphDeleteConfirmForm(forms.Form):
    CHOICES = (
        (1, _("Yes")),
        (0, _("No")),
    )
    confirm = forms.ChoiceField(label=_("Are you sure you want to delete " \
                                        "this whole graph?"),
                                help_text=_("This can take a few minutes"),
                                choices=CHOICES, required=True,
                                widget=forms.RadioSelect())


class GraphCloneForm(GraphForm):
    CHOICES = (
        ("schema", _("Schema")),
        ("data", _("Data")),
    )
    options = forms.MultipleChoiceField(required=False,
                                        widget=forms.widgets.CheckboxSelectMultiple,
                                        choices=CHOICES,
                                        initial=[c[0] for c in CHOICES],
                                        label=_("Which parts of the graph " \
                                                "would you like to clone?"))

    class Meta(GraphForm.Meta):
        exclude = ("name", "description", "relaxed", "public",)


class AddCollaboratorForm(forms.Form):
    new_collaborator = forms.ChoiceField(choices=User.objects.none(),
                        widget=forms.Select(attrs={'class': 'chzn-select'}),
                        label=_("Collaborator"))

    def __init__(self, *args, **kwargs):
        anonymous_name = _("Any User")
        graph = kwargs.pop("graph", None)
        collaborators = kwargs.pop("collaborators", [])
        super(AddCollaboratorForm, self).__init__(*args, **kwargs)
        if graph:
            users = User.objects.all().exclude(pk=settings.ANONYMOUS_USER_ID)
            no_collaborators = [
                (u.id, ((u.id != -1) and u.username or anonymous_name)) \
                for u in users \
                if u != graph.owner and u not in collaborators]
            self.fields["new_collaborator"].choices = no_collaborators
