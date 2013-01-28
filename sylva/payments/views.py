# -*- encoding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from accounts.models import Account

from zebra.forms import StripePaymentForm

from payments.models import StripeCustomer, StripePlan, StripeSubscription
from payments.forms import UnsubscribeForm

import stripe


logger = logging.getLogger('payments')


@login_required
def subscription_create(request, plan_name=''):
    user = request.user
    profile = user.get_profile()
    account_name = profile.account.name
    is_subscribed = account_name == 'Basic' or account_name == 'Premium'
    if is_subscribed:
        messages.info(request, _('You are already subscribed for a %s plan.'
                                                            % account_name))
        return redirect(reverse('dashboard'))
    customer = None
    stripe_errors = False
    error_msg = _('Sorry, an error occurred while processing the card. Your '
                  'payment could not be processed.')
    form = StripePaymentForm()
    if request.method == 'POST':
        form = StripePaymentForm(request.POST)
        if form.is_valid():
            stripe_token = form.cleaned_data['stripe_token']
            try:
                user.stripe_customer
            except ObjectDoesNotExist:
                try:
                    customer = StripeCustomer.objects.create(user=user,
                                                             card=stripe_token)
                    plan = StripePlan.objects.get(stripe_plan_id=slugify(plan_name))
                    StripeSubscription.objects.create(customer=customer,
                                                      plan=plan)
                except stripe.CardError, e:
                    stripe_errors = True
                    error = e.json_body['error']
                    if error['code'] in ['missing', 'processing_error']:
                        messages.error(request, error_msg)
                        logger.info('payments: %s: (%s) %s' %
                            (error['type'], error['code'], error['message']))
                    else:
                        messages.error(request, error['message'])
                except (stripe.InvalidRequestError,
                        stripe.AuthenticationError,
                        stripe.APIConnectionError,
                        stripe.StripeError), e:
                    stripe_errors = True
                    error = e.json_body['error']
                    messages.error(request, error_msg)
                    logger.info('payments: %s: %s' %
                                (error['type'], error['message']))
            if stripe_errors:
                if customer:
                    customer.delete()
            else:
                profile = user.get_profile()
                try:
                    account = Account.objects.get(name=plan_name)
                except Account.DoesNotExist:
                    messages.error(request, error_msg)
                    return redirect(reverse('dashboard'))
                profile.account = account
                profile.save()
                return redirect(reverse('subscription_welcome'))
    return render_to_response('payments/subscription_create.html',
                              {'form': form,
                               'plan_name': plan_name,
                               'publishable': settings.STRIPE_PUBLISHABLE},
                              context_instance=RequestContext(request))


@login_required
def subscription_cancel(request):
    user = request.user
    profile = user.get_profile()
    account_name = profile.account.name
    is_subscribed = account_name == 'Basic' or account_name == 'Premium'
    if not is_subscribed:
        return redirect(reverse('dashboard'))
    customer = None
    stripe_errors = False
    error_msg = _('Sorry, an error occurred while cancelling your '
                  'subscription. Please, contact us and we will try to solve '
                  'your problem as soon as possible.')
    try:
        customer = user.stripe_customer
    except ObjectDoesNotExist:
        return redirect(reverse('dashboard'))
    form = UnsubscribeForm()
    if request.method == 'POST':
        form = UnsubscribeForm(request.POST)
        if form.is_valid():
            try:
                stripe_customer = customer.stripe_customer
                stripe_customer.cancel_subscription()
            except (stripe.InvalidRequestError,
                    stripe.AuthenticationError,
                    stripe.APIConnectionError,
                    stripe.StripeError), e:
                stripe_errors = True
                error = e.json_body['error']
                logger.info('payments: %s: %s' %
                            (error['type'], error['message']))
            if not stripe_errors:
                profile = user.get_profile()
                try:
                    account = Account.objects.get(name='Free')
                except Account.DoesNotExist:
                    messages.error(request, error_msg)
                    return redirect(reverse('dashboard'))
                profile.account = account
                profile.save()
                customer.delete()
                messages.success(request, 'You have successfully unsubscribed')
                return redirect(reverse('dashboard'))
            else:
                messages.error(request, error_msg)
    return render_to_response('payments/subscription_cancel.html',
                              {'form': form},
                              context_instance=RequestContext(request))


@login_required
def subscription_welcome(request):
    user = request.user
    profile = user.get_profile()
    account_name = profile.account.name
    is_subscribed = account_name == 'Basic' or account_name == 'Premium'
    if not is_subscribed:
        return redirect(reverse('dashboard'))
    return render_to_response('payments/subscription_welcome.html',
                              {'user': user,
                               'account_name': account_name},
                              context_instance=RequestContext(request))
