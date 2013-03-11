# -*- encoding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from base.decorators import is_enabled, is_subscribed
from engines.gdb.utils import deploy
from payments.forms import SubscriptionForm, UnsubscriptionForm
from payments.models import StripeSubscriptionException


@is_enabled(settings.ENABLE_PAYMENTS)
@login_required
def subscription_edit_create(request, plan_id=''):
    user = request.user
    stripe_errors = False
    error_message = _('Sorry, an error occurred while processing the '
                      'card. Your payment could not be processed.')
    form = SubscriptionForm()
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription, stripe_errors, error_message = \
                form.stripe_edit_create_subscription(user, plan_id)
            if stripe_errors or not subscription:
                messages.error(request, error_message)
            else:
                if plan_id == '3':  # Premium
                    try:
                        #TODO: Add support for other backends in the form
                        engine = 'engines.gdb.backends.neo4j'
                        user = subscription.customer.user
                        instance = deploy(engine, request, user)
                        subscription.instance = instance
                        subscription.save()
                    except:
                        stripe_errors = True
                        # TODO: destroy the corrupt instance
                        subscription.customer.delete()
                        messages.error(request, error_message)
                if not stripe_errors:
                    try:
                        subscription.update_stripe_subscription()
                        return redirect('subscription_welcome')
                    except StripeSubscriptionException:
                        subscription.customer.delete()
                        messages.error(request, error_message)
    return render_to_response('payments/subscription_edit_create.html',
                              {'form': form,
                               'plan_name': settings.STRIPE_PLANS[plan_id]['name'],
                               'publishable': settings.STRIPE_PUBLISHABLE},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_PAYMENTS)
@login_required
@is_subscribed
def subscription_cancel(request):
    user = request.user
    customer = None
    stripe_errors = False
    error_message = _('Sorry, an error occurred while cancelling your '
                      'subscription. Please, contact us and we will '
                      'try to solve your problem as soon as possible.')
    customers = user.stripe_customers.all()
    if not customers:
        return redirect('dashboard')
    form = UnsubscriptionForm()
    if request.method == 'POST':
        form = UnsubscriptionForm(request.POST)
        if form.is_valid():
            customer = customers[0]
            stripe_errors = form.stripe_cancel_subscription(customer)
            if stripe_errors:
                messages.error(request, error_message)
            else:
                customer.delete()
                messages.success(request, _('You have successfully unsubscribed'))
                return redirect('dashboard')
    return render_to_response('payments/subscription_cancel.html',
                              {'form': form},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_PAYMENTS)
@login_required
@is_subscribed
def subscription_welcome(request):
    user = request.user
    account = user.get_profile().account
    return render_to_response('payments/subscription_welcome.html',
                              {'user': user,
                               'account_name': account.name},
                              context_instance=RequestContext(request))


@is_enabled(settings.ENABLE_PAYMENTS)
def subscription_plans(request):
    user = request.user
    account_type = None
    is_basic = None
    is_premium = None
    basic_plan = settings.STRIPE_PLANS['2']
    premium_plan = settings.STRIPE_PLANS['3']
    if user.is_authenticated():
        account_type = user.get_profile().account.type
        is_basic = account_type == 2
        is_premium = account_type == 3
    return render_to_response('payments/plans.html',
                              {'basic_plan': basic_plan,
                               'premium_plan': premium_plan,
                               'is_basic': is_basic,
                               'is_premium': is_premium},
                              context_instance=RequestContext(request))
