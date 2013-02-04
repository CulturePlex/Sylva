# -*- coding: utf-8 -*-

from django.utils.functional import wraps
from django.shortcuts import redirect


def is_enable(setting=False, next='index'):
    def _is_enable(view):
        def _decorator(request, *args, **kwargs):
            if setting:
                return view(request, *args, **kwargs)
            else:
                return redirect(next)
        return wraps(view)(_decorator)
    return _is_enable
