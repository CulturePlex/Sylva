# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from userena.models import UserenaLanguageBaseProfile


class Account(models.Model):
    name = models.CharField(_('name'), max_length=255)
    TYPE_CHOICES = (
        (1, _('Free')),
        (2, _('Basic')),
        (3, _('Premium')),
    )
    type = models.PositiveSmallIntegerField(_('type'),
                                              choices=TYPE_CHOICES,
                                              blank=True,
                                              null=True)
    graphs = models.IntegerField(_('graphs'), blank=True, null=True)
    nodes = models.IntegerField(_('nodes'), blank=True, null=True)
    relationships = models.IntegerField(_('relationships'), blank=True,
                                        null=True)
    storage = models.IntegerField(_('storage'), blank=True, null=True,
                                  help_text=_('bytes'))
    queries = models.IntegerField(_('queries'), blank=True, null=True,
                                  help_text=_('Queries per day'))
    privacy = models.NullBooleanField(_('privacy'), blank=True, null=True,
                                  default=False,
                                  help_text=_('Can change graphs\' privacy?'))

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.get_type_display().lower())


class UserProfile(UserenaLanguageBaseProfile):
    GENDER_CHOICES = (
        (1, _('Male')),
        (2, _('Female')),
    )
    gender = models.PositiveSmallIntegerField(_('gender'),
                                              choices=GENDER_CHOICES,
                                              blank=True,
                                              null=True)
    website = models.URLField(_('website'), blank=True, verify_exists=False)
    location = models.CharField(_('location'), max_length=255, blank=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    about_me = models.TextField(_('about me'), blank=True)
    institution = models.CharField(_('institution'), blank=True, null=True,
                                  max_length=150)
    company = models.CharField(_('company'), blank=True, null=True,
                               max_length=150)
    lab = models.CharField(_('laboratoy'), blank=True, null=True,
                           max_length=150)
    options = models.TextField(_('options'), null=True, blank=True)
    user = models.OneToOneField(User, verbose_name=_('user'))
    account = models.ForeignKey(Account, verbose_name=_('account'),
                                related_name="users")

    class Meta:
        permissions = (
            ('view_profile', _('View profile')),
            ('change_profile', _('Change profile')),
            ('delete_profile', _('Delete profile')),
        )

    @property
    def age(self):
        if not self.birth_date:
            return False
        else:
            today = datetime.date.today()
            # Raised when birth date is February 29 and the current year is not
            # a leap year.
            try:
                birthday = self.birth_date.replace(year=today.year)
            except ValueError:
                day = today.day - 1 if today.day != 1 else today.day + 2
                birthday = self.birth_date.replace(year=today.year, day=day)
            if birthday > today:
                return today.year - self.birth_date.year - 1
            else:
                return today.year - self.birth_date.year


@receiver(post_save, sender=User)
def create_profile_account(*args, **kwargs):
    user = kwargs.get("instance", None)
    created = kwargs.get("created", False)
    if user and created:
        try:
            user.get_profile().account
        except UserProfile.DoesNotExist:
            accounts = Account.objects.filter(type=1)
            if not accounts:
                account = Account.objects.create(**settings.ACCOUNT_FREE)
            else:
                account = accounts[0]
            UserProfile.objects.create(user=user, account=account)
