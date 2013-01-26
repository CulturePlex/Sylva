# -*- encoding: utf-8 -*-
from django.contrib import admin

from payments.forms import StripeCustomerAdminForm, StripeSubscriptionAdminForm
from payments.models import StripeCustomer, StripePlan, StripeSubscription


class StripeCustomerAdmin(admin.ModelAdmin):
    form = StripeCustomerAdminForm


class StripePlanAdmin(admin.ModelAdmin):
    pass


class StripeSubscriptionAdmin(admin.ModelAdmin):
    form = StripeSubscriptionAdminForm

admin.site.register(StripeCustomer, StripeCustomerAdmin)
admin.site.register(StripePlan, StripePlanAdmin)
admin.site.register(StripeSubscription, StripeSubscriptionAdmin)
