# -*- coding: utf-8 -*-
from django.utils.functional import wraps
from django.shortcuts import redirect


def is_enabled(setting=False, next='index'):
    def _is_enabled(view):
        def _decorator(request, *args, **kwargs):
            if setting:
                return view(request, *args, **kwargs)
            else:
                return redirect(next)
        return wraps(view)(_decorator)
    return _is_enabled


def is_subscribed(view):
    def _decorator(request, *args, **kwargs):
        user = request.user
        account = user.get_profile().account
        is_subscribed = account.type != 1
        if not is_subscribed:
            return redirect('dashboard')
        return view(request, *args, **kwargs)
    return wraps(view)(_decorator)
