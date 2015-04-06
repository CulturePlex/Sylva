from django.forms import ModelForm
from models import ReportTemplate


class ReportTemplateForm(ModelForm):
    class Meta:
        model = ReportTemplate
        fields = "__all__"
