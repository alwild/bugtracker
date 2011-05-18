from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django import forms
import os.path

class Status (models.Model):
    title = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.title

class StatusForm (ModelForm):
    class Meta:
        model = Status
 
class Category (models.Model):
    title = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.title

class CategoryForm (ModelForm):
    class Meta:
        model = Category
        
class Severity (models.Model):
    title = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.title
    
class SeverityForm (ModelForm):
    class Meta:
        model = Severity           

class Project (models.Model):
    title = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.title
    
class ProjectForm (ModelForm):
    class Meta:
        model = Project
    
class Issue (models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now=True)
    updated_date = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(Status)
    severity = models.ForeignKey(Severity)
    category = models.ForeignKey(Category, blank=True, null=True)
    project = models.ForeignKey(Project)
    assigned_user = models.ForeignKey(User, related_name='Assigned_User')
    created_user = models.ForeignKey(User, related_name='Created_User')
    watchers = models.ManyToManyField(User, related_name='Watchers', blank=True)
    estimated_time = models.DecimalField(decimal_places = 2, max_digits = 18, blank=True, null=True)
    
    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('bugtracker.issues.views.issue_details', [str(self.id)])
    
    def get_email_subject(self):
        return "%s Issue %s has been updated" % (self.project, self.id)
    
class IssueForm (ModelForm):
    class Meta:
        model = Issue
        fields = ('title', 'description', 'status', 'assigned_user', 'estimated_time', 'severity', 'category', 'project', 'watchers')
    file = forms.FileField(required=False)
        
class IssueHistory (models.Model):
    issue = models.ForeignKey(Issue)
    status = models.ForeignKey(Status, blank=True, null=True)
    severity = models.ForeignKey(Severity, blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    project = models.ForeignKey(Project, blank=True, null=True)
    assigned_user = models.ForeignKey(User, related_name='History_Assigned_User', blank=True, null=True)
    created_user = models.ForeignKey(User, related_name='History_Created_User', blank=True, null=True)
    note = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now=True)
    time_spent = models.DecimalField(decimal_places = 2, max_digits = 18, blank=True, null=True)
    
    def __unicode__(self):
        return self.note

class IssueHistoryForm (ModelForm):
    class Meta:
        model = IssueHistory
        fields = ('status', 'note', 'time_spent', 'assigned_user', 'severity', 'category', 'project')
    file = forms.FileField(required=False)
    
class Attachment (models.Model):
    issue = models.ForeignKey(Issue)
    file = models.FileField(upload_to='uploads')
    
    def __unicode__(self):
        return os.path.basename(self.file.name)
    
class AttachmentForm (ModelForm):
    class Meta:
        model = Attachment
        fields = ('file',)
