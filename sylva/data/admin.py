# -*- coding: utf-8 -*-
from django.contrib import admin

from data.models import (Data, MediaFile, MediaLink)


admin.site.register(Data)
admin.site.register(MediaFile)
admin.site.register(MediaLink)
