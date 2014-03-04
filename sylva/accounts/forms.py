# -*- coding: utf-8 -*-
import datetime

from django import forms
from userena.forms import EditProfileForm


class UserProfileEditForm(EditProfileForm):

    def __init__(self, *args, **kwargs):
        super(UserProfileEditForm, self).__init__(*args, **kwargs)
        for field_name in ["account", "options", "privacy"]:
            del self.fields[field_name]

    def clean_birth_date(self):
        birth_date = self.cleaned_data["birth_date"]
        today = datetime.date.today()
        if birth_date > today:
            raise forms.ValidationError("You need to introduce a past date.")
        else:
            return birth_date
