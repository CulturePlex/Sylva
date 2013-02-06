# -*- encoding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from base.decorators import is_enable

from accounts.models import Account

from payments.forms import SubscriptionForm, UnsubscriptionForm


@is_enable(settings.ENABLE_PAYMENTS)
@login_required
def subscription_create(request, plan_name=''):
    user = request.user
    profile = user.get_profile()
    stripe_errors = False
    error_message = _('Sorry, an error occurred while processing the '
                      'card. Your payment could not be processed.')
    form = SubscriptionForm()
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            account = None
            try:
                account = Account.objects.get(name=plan_name)
            except Account.DoesNotExist:
                messages.error(request, error_message)
                return redirect('dashboard')
            stripe_errors, error_message = \
                            form.stripe_create_subscription(user, plan_name)
            if stripe_errors:
                messages.error(request, error_message)
            else:
                profile = user.get_profile()
                profile.account = account
                profile.save()
                return redirect('subscription_welcome')
    return render_to_response('payments/subscription_create.html',
                              {'form': form,
                               'plan_name': plan_name,
                               'publishable': settings.STRIPE_PUBLISHABLE},
                              context_instance=RequestContext(request))


@is_enable(settings.ENABLE_PAYMENTS)
@login_required
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


@is_enable(settings.ENABLE_PAYMENTS)
@login_required
def subscription_welcome(request):
    user = request.user
    profile = user.get_profile()
    account_name = profile.account.name
    is_subscribed = account_name == 'Basic' or account_name == 'Premium'
    if not is_subscribed:
        return redirect('dashboard')
    return render_to_response('payments/subscription_welcome.html',
                              {'user': user,
                               'account_name': account_name},
                              context_instance=RequestContext(request))
