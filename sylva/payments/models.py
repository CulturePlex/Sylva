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


# Stripe integrations

class StripeCustomer(DatesModelBase, ZebraStripeCustomer):
    '''
    A new customer is always created on Stripe, even using both the same
    card and email. So, if the user is subscribed for a Premium account, then
    unsubscribed, and then subscribed again using both the same card and
    email, a new customer will be created on Stripe.
    '''
    user = models.OneToOneField(User, verbose_name=_('User'),
                                related_name='stripe_customer')
    card = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = _('StripeCustomer')
        verbose_name_plural = _('StripeCustomers')

    def save(self, *args, **kwargs):
        customer = None
        try:
            customer = stripe.Customer.create(card=self.card,
                                              email=str(self.user.email))
        except stripe.InvalidRequestError:
            logger.error("payments: you must supply a valid card: %s"
                                                        % self.card)
        if customer:
            self.stripe_customer_id = customer.id
            super(StripeCustomer, self).save(*args, **kwargs)


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

    class Meta:
        verbose_name = _('StripeSubscription')
        verbose_name_plural = _('StripeSubscriptions')

    def save(self, *args, **kwargs):
        customer = self.customer.stripe_customer
        customer.update_subscription(plan=self.plan.stripe_plan_id,
                                     prorate="True")
        super(StripeSubscription, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s: %s" % (self.customer, self.plan)

    @property
    def stripe_customer(self):
        return self.customer.stripe_customer


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
