# -*- encoding: utf-8 -*-
import logging
import settings

from django import forms
from django.utils.translation import ugettext_lazy as _

from zebra.forms import StripePaymentForm

from payments.models import (StripeCustomer, StripeSubscription, StripePlan,
                             StripeCustomerException,
                             StripeSubscriptionException)

import stripe


logger = logging.getLogger('payments')


class SubscriptionForm(StripePaymentForm):

    def stripe_edit_create_subscription(self, user, plan_id):
        customer = None
        stripe_errors = False
        error_message = ''
        stripe_token = self.cleaned_data['stripe_token']
        customers = user.stripe_customers.all()
        try:
            plan = StripePlan.objects.get(stripe_plan_id=plan_id)
        except StripePlan.DoesNotExist:
            stripe_errors = True
            error_message = _('This plan does not exist')
        if not stripe_errors:
            subscription_updated = False
            if len(customers) == 1:
                customer = customers[0]
                account_type = settings.STRIPE_PLANS[plan_id]['account_type']
                if user.get_profile().account.type != account_type:
                    subscription = customer.stripe_subscription
                    subscription.plan = plan
                    subscription.save()
                    subscription_updated = True
            elif len(customers) > 1 and plan_id == '2':
                stripe_errors = True
                error_message = _('You need to cancel your %s subscriptions '
                                  'before subscribing for a %s plan' %
                                        (settings.STRIPE_PLANS['3']['name'],
                                         settings.STRIPE_PLANS['2']['name']))
            if not stripe_errors and not subscription_updated:
                try:
                    customer = StripeCustomer.objects.create(user=user,
                                                             card=stripe_token)
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
