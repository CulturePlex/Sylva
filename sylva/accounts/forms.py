# -*- coding: utf-8 -*-
from userena.forms import EditProfileForm


class UserProfileEditForm(EditProfileForm):

    def __init__(self, *args, **kwargs):
        super(UserProfileEditForm, self).__init__(*args, **kwargs)
        for field_name in ["account", "options", "privacy"]:
            del self.fields[field_name]
