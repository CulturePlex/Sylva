# -*- encoding: utf-8 -*-
import settings
import logging

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string

from accounts.models import Account

from engines.models import Instance

from zebra.models import StripeCustomer as ZebraStripeCustomer
from zebra.models import StripePlan as ZebraStripePlan
from zebra.models import StripeSubscription as ZebraStripeSubscription

from zebra.signals import (zebra_webhook_customer_subscription_created,
                           zebra_webhook_customer_subscription_deleted)

import stripe


logger = logging.getLogger('payments')


class DatesModelBase(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class StripeCustomer(DatesModelBase, ZebraStripeCustomer):
    '''
    A new customer is always created on Stripe, even using both the same
    card and email. So, if the user is subscribed for a Premium account, then
    unsubscribed, and then subscribed again using both the same card and
    email, a new customer will be created on Stripe.
    '''
    user = models.ForeignKey(User, verbose_name=_('User'),
                             related_name='stripe_customers')
    card = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = _('StripeCustomer')
        verbose_name_plural = _('StripeCustomers')

    def save(self, *args, **kwargs):
        stripe_customer = None
        stripe_errors = False
        error_message = _('Sorry, an error occurred while processing the '
                          'card. Your payment could not be processed.')
        try:
            stripe_customer = stripe.Customer.create(card=self.card,
                                                     email=str(self.user.email))
        except stripe.CardError, e:
            stripe_errors = True
            error = e.json_body['error']
            logger.info('payments (customer): %s: (%s) %s' %
                               (error['type'], error['code'], error['message']))
            if error['code'] not in ['missing', 'processing_error']:
                error_message = error['message']
        except (stripe.InvalidRequestError,
                stripe.AuthenticationError,
                stripe.APIConnectionError,
                stripe.StripeError), e:
            stripe_errors = True
            error = e.json_body['error']
            logger.info('payments (customer): %s: %s' %
                                (error['type'], error['message']))
        except Exception:
            stripe_errors = True
            logger.info('payments (customer): Unexpected error')

        if stripe_errors:
            raise StripeCustomerException(error_message)

        if stripe_customer:
            self.stripe_customer_id = stripe_customer.id
            super(StripeCustomer, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        user = self.user
        customers = user.stripe_customers.all()
        if len(customers) == 1:
            try:
                profile = user.get_profile()
                account = Account.objects.get(type=1)
                profile.account = account
                profile.save()
            except Exception:
                pass
        super(StripeCustomer, self).delete(*args, **kwargs)


class StripePlan(DatesModelBase, ZebraStripePlan):
    account = models.OneToOneField(Account,
                                   verbose_name=_('Account'),
                                   related_name='stripe_plan')

    class Meta:
        verbose_name = _('StripePlan')
        verbose_name_plural = _('StripePlans')


class StripeSubscription(DatesModelBase, ZebraStripeSubscription):
    customer = models.OneToOneField(StripeCustomer,
                                    verbose_name=_('StripeCustomer'),
                                    related_name='stripe_subscription')
    plan = models.ForeignKey(StripePlan, verbose_name=_('Plan'),
                             related_name='stripe_subscriptions')
    instance = models.OneToOneField(Instance,
                                    verbose_name=_('Instance'),
                                    related_name='stripe_subscription',
                                    null=True)

    class Meta:
        verbose_name = _('StripeSubscription')
        verbose_name_plural = _('StripeSubscriptions')

    def __unicode__(self):
        return u"%s (%s)" % (self.customer, self.plan)

    @property
    def stripe_customer(self):
        return self.customer.stripe_customer

    def save(self, *args, **kwargs):
        '''A customer can be subscribed for 1 Basic plan or N Premium plans'''
        new_customer = self.customer
        user = new_customer.user
        stripe_customer = new_customer.stripe_customer
        stripe_errors = False
        error_message = _('Sorry, an error occurred while processing the '
                          'card. Your payment could not be processed.')
        profile = user.get_profile()
        stripe_plan_id = self.plan.stripe_plan_id
        account_type = settings.STRIPE_PLANS[stripe_plan_id]['account_type']
        customers = user.stripe_customers.exclude(stripe_subscription__isnull=True)
        if len(customers) == 1:  # the user is already subscribed for a plan
            if profile.account.type == account_type == 2:  # is Basic plan
                new_customer.delete()
                error_message = _('You are already subscribed for a %s plan' %
                                            settings.STRIPE_PLANS['2']['name'])
                raise StripeSubscriptionException(error_message)
        try:
            stripe_customer.update_subscription(plan=stripe_plan_id,
                                                prorate="True")
        except (stripe.InvalidRequestError,
                stripe.AuthenticationError,
                stripe.APIConnectionError,
                stripe.StripeError), e:
            stripe_errors = True
            error = e.json_body['error']
            logger.info('payments (subscription): %s: %s' %
                                (error['type'], error['message']))
        except Exception:
            stripe_errors = True
            logger.info('payments (subscription): Unexpected error')

        if stripe_errors:
            raise StripeSubscriptionException(error_message)

        if profile.account.type != account_type:
            try:
                account = Account.objects.get(type=account_type)
                profile.account = account
                profile.save()
            except Account.DoesNotExist:
                raise StripeSubscriptionException(error_message)

        super(StripeSubscription, self).save(*args, **kwargs)


# Custom exceptions

class StripeCustomerException(Exception):
    pass


class StripeSubscriptionException(Exception):
    pass


# Stripe Webhooks

@receiver(zebra_webhook_customer_subscription_created,
          dispatch_uid="payments.process_subscription_created_event")
def process_subscription_created_event(sender, **kwargs):
    subject = "SylvaDB subscription"
    template = "payments/subscription_created.txt"
    process_stripe_event("subscription_created", subject, template, **kwargs)


@receiver(zebra_webhook_customer_subscription_deleted,
          dispatch_uid="payments.process_subscription_deleted_event")
def process_subscription_deleted_event(sender, **kwargs):
    subject = "SylvaDB unsubscription"
    template = "payments/subscription_deleted.txt"
    process_stripe_event("subscription_deleted", subject, template, **kwargs)


def process_stripe_event(event_type, subject, template, **kwargs):
    received = False
    customer = None
    plan_name = ''
    full_json = kwargs.pop("full_json")
    if full_json:
        data = full_json.get("data")
        if data:
            obj = data.get("object")
            if obj:
                stripe_customer_id = obj.get("customer")
                plan = obj.get("plan")
                if plan:
                    plan_name = plan.get("name")
                if stripe_customer_id:
                    received = True
                    try:
                        customer = stripe.Customer.retrieve(stripe_customer_id)
                    except stripe.InvalidRequestError:
                        logger.error("payments: No such Stripe customer: %s"
                                                        % stripe_customer_id)
                    if customer:
                        email = customer['email']
                        send_payments_email(email, plan_name, subject, template)
    if not received:
        logger.error("payments: JSON data for the Stripe Webhook '%s' "
                     "could not be processed." % (event_type))


def send_payments_email(email, plan_name, subject, template):
    user = None
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.error("payments: No such user with this email: %s" % email)
    if user:
        from_email = settings.DEFAULT_FROM_EMAIL
        message = render_to_string(template, {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'username': user.username,
            'plan_name': plan_name
        })
        fail_silently = not settings.DEBUG
        send_mail(subject, message, from_email, [user.email],
                  fail_silently=fail_silently)
