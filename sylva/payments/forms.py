import logging

from django import forms
from django.template.defaultfilters import slugify

from zebra.forms import StripePaymentForm

from payments.models import (StripeCustomer, StripeSubscription, StripePlan,
                             StripeCustomerException,
                             StripeSubscriptionException)

import stripe


logger = logging.getLogger('payments')


class SubscriptionForm(StripePaymentForm):

    def stripe_create_subscription(self, user, plan_name):
        customer = None
        stripe_errors = False
        error_message = ''
        stripe_token = self.cleaned_data['stripe_token']
        try:
            customer = StripeCustomer.objects.create(user=user,
                                                     card=stripe_token)
            plan = StripePlan.objects.get(stripe_plan_id=slugify(plan_name))
            StripeSubscription.objects.create(customer=customer,
                                              plan=plan)
        except (StripeCustomerException,
                StripeSubscriptionException), e:
            stripe_errors = True
            error_message = e.message

        return stripe_errors, error_message


class UnsubscriptionForm(forms.Form):

    def stripe_cancel_subscription(self, customer):
        stripe_errors = False
        try:
            stripe_customer = customer.stripe_customer
            stripe_customer.cancel_subscription()
        except (stripe.InvalidRequestError,
                stripe.AuthenticationError,
                stripe.APIConnectionError,
                stripe.StripeError), e:
            stripe_errors = True
            error = e.json_body['error']
            logger.info('payments (subscription): %s: %s' %
                                (error['type'], error['message']))

        return stripe_errors


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
