from django.contrib import admin
from models import ReportTemplate, Report


class ReportTemplateAdmin(admin.ModelAdmin):
	pass


class ReportAdmin(admin.ModelAdmin):
	pass 


admin.site.register(ReportTemplate, ReportTemplateAdmin)
admin.site.register(Report, ReportAdmin)
