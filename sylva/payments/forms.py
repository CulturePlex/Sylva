from django import forms

from payments.models import StripeCustomer, StripeSubscription


class UnsubscribeForm(forms.Form):
    pass


class StripeCustomerAdminForm(forms.ModelForm):

    class Meta:
        model = StripeCustomer

    def __init__(self, *args, **kwargs):
        super(StripeCustomerAdminForm, self).__init__(*args, **kwargs)


class StripeSubscriptionAdminForm(forms.ModelForm):

    class Meta:
        model = StripeSubscription

    def __init__(self, *args, **kwargs):
        super(StripeSubscriptionAdminForm, self).__init__(*args, **kwargs)
