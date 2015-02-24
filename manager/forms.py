__author__ = 'Yoanis Gil'

from django import forms
from django.forms import ModelChoiceField
from django.utils.translation import ugettext as _
from models import ApplicationTemplate, Repository


class ApplicationTemplateModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class NewApplicationForm(forms.Form):
    application_name = forms.CharField(label=_("Application name"), max_length=255)
    repository_url = forms.CharField(label=_("Repository URL"), max_length=255)
    repository_type = forms.ChoiceField(widget=forms.RadioSelect, choices=Repository.TYPES)
    application_template = ApplicationTemplateModelChoiceField(queryset=ApplicationTemplate.objects.all())


class NewApplicationBuildForm(forms.Form):
    branch = forms.CharField(label=_("Build branch"))