from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext
from django.utils import simplejson
from django.contrib import messages
from bugtracker.issues.models import *
from bugtracker.issues.forms import SearchForm
from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import datetime
from django.template.loader import render_to_string
from bugtracker import settings

def index(request):
    if request.user.is_active:
        return redirect('/issues/my/')
    return redirect('/accounts/login/')

def search(request):
    searchform = SearchForm(request.GET)
    
    issue_list = get_search_results(searchform)
    
    if request.GET.get('sort'):
        issue_list = issue_list.extra(order_by = [request.GET['sort']])
    
    paginator = Paginator(issue_list, 20)
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    # If page request (9999) is out of range, deliver last page of results.
    try:
        issues = paginator.page(page)
    except (EmptyPage, InvalidPage):
        issues = paginator.page(paginator.num_pages)
    
    c = { 'form' : searchform, 'issues' : issues, 'title' : 'Search'}
    
    return issues_render_to_response('issues/search.html', c, request)

def get_search_results(searchform):
    query = Issue.objects.all()
    
    if searchform.is_valid():
        
        if searchform.cleaned_data['issue_id']:
            query = query.filter(id=searchform.cleaned_data['issue_id'])
        
        if searchform.cleaned_data['title']:
            query = query.filter(title__icontains=searchform.cleaned_data['title'])
        
        if searchform.cleaned_data['assigned_user']:
            query = query.filter(assigned_user__in=searchform.cleaned_data['assigned_user'])
            
        if searchform.cleaned_data['created_user']:
            query = query.filter(created_user__in=searchform.cleaned_data['created_user'])
            
        if searchform.cleaned_data['status']:
            query = query.filter(status__in=searchform.cleaned_data['status'])
        
        if searchform.cleaned_data['project']:
            query = query.filter(project__in=searchform.cleaned_data['project'])
        
        if searchform.cleaned_data['category']:
            query = query.filter(category__in=searchform.cleaned_data['category'])
            
        if searchform.cleaned_data['severity']:
            query = query.filter(severity__in=searchform.cleaned_data['severity'])
            
        if searchform.cleaned_data['updated_date']:
            query = query.filter(updated_date__gte=searchform.cleaned_data['updated_date'])
        
        if searchform.cleaned_data['created_date']:
            query = query.filter(created_date__gte=searchform.cleaned_data['created_date'])
            
    return query

@login_required
def lookups(request):
    model = eval(request.GET['model_type'])
    lookups = model.objects.all()
    form_class = eval(model.__name__ + 'Form')
    form = form_class() 
    c = {'lookups' : lookups, 'form' : form, 'model_type' : model.__name__}
    return issues_render_to_response('issues/lookups.html', c, request)

@login_required
def lookups_create(request):
    if request.method == "POST":
        model = eval(request.GET['model_type'])
        form_class = eval(model.__name__ + 'Form')
        form = form_class(request.POST) 
        form.save()
        
        msg = ugettext("The " + model.__name__ + " was created successfully.")
        messages.success(request, msg, fail_silently=True)
    
    redir = redirect(lookups)
    redir['Location'] += '?model_type=' + model.__name__
    return redir
    
@csrf_exempt
@login_required
def lookups_delete(request):
    if request.method == "POST":
        model = eval(request.GET['model_type'])
        lookup = model.objects.get(pk=request.POST["id"])
        lookup.delete()
    return HttpResponse(simplejson.dumps({'result' : 'success'}), mimetype='application/javascript')
  
@login_required
def my_issues(request):
    issue_list = Issue.objects.filter(assigned_user=request.user)
    
    if request.GET.get('sort'):
        issue_list = issue_list.extra(order_by = [request.GET['sort']])
    
    paginator = Paginator(issue_list, 20)
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    # If page request (9999) is out of range, deliver last page of results.
    try:
        issues = paginator.page(page)
    except (EmptyPage, InvalidPage):
        issues = paginator.page(paginator.num_pages)
    
    return issues_render_to_response('issues/my.html', {'issues': issues, 'title' : 'My Issues'}, request)
  
@login_required  
def issue_create(request):
    if request.method == "POST":
        f = IssueForm(request.POST, request.FILES)
        
        if not f.is_valid():
            return issues_render_to_response('issues/issue_form.html', {'form' : f}, request)
        
        issue = f.save(commit = False)
        issue.created_user = request.user
        issue.save()
        
        if len(request.FILES) > 0:
            aform = AttachmentForm(request.POST, request.FILES)
            attachment = aform.save(commit = False)
            attachment.issue = issue;
            attachment.save()
        
        msg = ugettext("The Issue was created successfully.")
        messages.success(request, msg, fail_silently=True)
        
        email_body = render_to_string('issues/emails/created.html', {'user' : request.user, 'request' : request, 'issue' : issue})
        issues_send_email(issue, email_body, request.user)
        
        return redirect('/issues/create')
    else:
        f = IssueForm(initial = {'status' : 1, 'severity' : 5})
        c = {'form': f}
        c.update(csrf(request))
        return issues_render_to_response('issues/issue_form.html', c, request)
    
def issue_details(request, id):
    issue = Issue.objects.get(pk=id)
    form = IssueHistoryForm()
    return issues_render_to_response('issues/issue_details.html', 
                              {'issue' : issue, 'title' : issue.title, 'form' : form }, request)

@login_required
def issue_update(request, id):
    
    if request.method != "POST":
        redirect(search)
    
    form = IssueHistoryForm(request.POST, request.FILES)
    
    issue = Issue.objects.get(pk = id)
    
    if not form.is_valid():
        return issues_render_to_response('issues/issue_details.html', 
                          {'issue' : issue, 'title' : issue.title,'form' : form }, request)
    
    issuehistory = form.save(commit=False)
    
    issuehistory.issue = issue
    issuehistory.created_user = request.user
    issuehistory.save()
    
    if form.cleaned_data['assigned_user'] and form.cleaned_data['assigned_user'] != issue.assigned_user:
        issue.assigned_user = form.cleaned_data['assigned_user']
    
    if form.cleaned_data['status'] and form.cleaned_data['status'] != issue.status:
        issue.status = form.cleaned_data['status']
    
    if form.cleaned_data['severity'] and form.cleaned_data['severity'] != issue.severity:
        issue.status = form.cleaned_data['severity']
    
    if form.cleaned_data['category'] and form.cleaned_data['category'] != issue.category:
        issue.status = form.cleaned_data['category']
    
    if form.cleaned_data['project'] and form.cleaned_data['project'] != issue.project:
        issue.project = form.cleaned_data['project']
    
    issue.updated_date = datetime.datetime.now()
    issue.save()
    
    if len(request.FILES) > 0:
        aform = AttachmentForm(request.POST, request.FILES)
        attachment = aform.save(commit = False)
        attachment.issue = issue;
        attachment.save()
        
    msg = ugettext("The Issue was updated successfully.")
    messages.success(request, msg, fail_silently=True)
    
    email_body = render_to_string('issues/emails/updated.html', {'user' : request.user, 'request' : request, 'issuehistory' : issuehistory})
    issues_send_email(issue, email_body, request.user)
    
    return redirect(issue_details, id)

def issues_send_email(issue, email_body, user):
    #send email to assigned_user
    if issue.assigned_user != user:
        issue.assigned_user.email_user(issue.get_email_subject(), email_body, settings.SUPPORT_EMAIL)
    
    #send email to all watchers    
    for user_to in issue.watchers.all():
        if user_to != user and user_to != issue.assigned_user:
            user_to.email_user(issue.get_email_subject(), email_body, settings.SUPPORT_EMAIL)
    
def issues_render_to_response(template, dict, request):
    dict.update({'user' : request.user})
    dict.update({'request' : request})
    return render_to_response(template, dict, context_instance=RequestContext(request))    