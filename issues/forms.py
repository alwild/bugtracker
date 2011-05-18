from django import forms
from bugtracker.issues.models import Status
from bugtracker.issues.models import Category
from bugtracker.issues.models import Severity
from bugtracker.issues.models import Project
from django.contrib.auth.models import User

class SearchForm(forms.Form):
    title = forms.CharField(required=False)
    assigned_user = forms.ModelMultipleChoiceField(queryset = User.objects.all(), required=False)
    created_user = forms.ModelMultipleChoiceField(queryset = User.objects.all(), required=False)
    status = forms.ModelMultipleChoiceField(queryset = Status.objects.all(), required=False)
    category = forms.ModelMultipleChoiceField(queryset = Category.objects.all(), required=False)
    severity = forms.ModelMultipleChoiceField(queryset = Severity.objects.all(), required=False)
    project = forms.ModelMultipleChoiceField(queryset = Project.objects.all(), required=False)
    updated_date = forms.DateField(required=False)
    created_date = forms.DateField(required=False)
    issue_id = forms.IntegerField(required=False)