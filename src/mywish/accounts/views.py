from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.conf import settings
from django.utils.http import urlquote, base36_to_int
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login
from django.shortcuts import get_object_or_404, redirect
from django.template import Context, loader
from django.core.mail import EmailMessage
from mywish.accounts.forms import UserLoginForm, UserCreationForm, LoginAsForm
import mywish.utils
import datetime, mywish.settings
import base64, time

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

@csrf_exempt
def mylogin(request, template_name=None):
    try:
        redirect_to = request.GET['next']
    except KeyError:
        redirect_to = ''
        
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        
        if user is None:
            try:
                user_found = User.objects.get(email=request.POST['username'])
                user = authenticate(username=user_found.username, password=request.POST['password']) 
            except User.DoesNotExist:
                print 'user does not exist.'
            
        if user is not None:
            if user.is_active:
                login(request, user)
                # success
                base64Cookie = mywish.utils.get_token(user)

                response = HttpResponseRedirect('/')
                if  redirect_to != '':
                    response = HttpResponseRedirect(redirect_to)

                expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=1), "%a, %d-%b-%Y %H:%M:%S GMT")
                response.set_cookie(mywish.settings.MWTokenName, value=base64Cookie, expires=expires, domain='.localsnake.com')

                return response
            else:
                # disabled account
                return render_to_response(template_name, {'form' : form}, context_instance=RequestContext(request))
        else:
            # invalid login
            return render_to_response(template_name, {'form' : form}, context_instance=RequestContext(request))
    else:
        form = UserLoginForm()
        return render_to_response(template_name, {'form' : form}, context_instance=RequestContext(request))

@login_required
def mylogout(request, template_name='logged_out.html', next_page='/'):
    logout(request)
    response = redirect(next_page)
    response.delete_cookie(mywish.settings.MWTokenName, domain=".localsnake.com")
    return response
    #return direct_to_template(request, template_name) 
           
#from django.views.decorators.csrf import csrf_protect
@staff_member_required
def login_as(request, template_name="accounts/login_as.html"):
    if request.method == "POST":
        data = request.POST or None
        form = LoginAsForm(data, request=request)
        
        if form.is_valid():
            form.save()
            base64Cookie = mywish.utils.get_token(request.user)
            expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(days=1), "%a, %d-%b-%Y %H:%M:%S GMT")
            response = HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            response.set_cookie(mywish.settings.MWTokenName, value=base64Cookie, expires=expires, domain='.localsnake.com')            
            
            return response
    else:
        form = LoginAsForm(request=request)
    
    return render_to_response(template_name, {'form': form, 'site_name':Site.objects.get_current().name, }, 
                              context_instance=RequestContext(request))
    
#@csrf_protect
@csrf_exempt
def signup(request, template_name='accounts/signup.html', 
           email_template_name='registration/signup_email.html',
           signup_form=UserCreationForm,
           token_generator=default_token_generator,
           post_signup_redirect=None):
    if post_signup_redirect is None:
        post_signup_redirect = reverse('mywish.accounts.views.signup_done')
        
    if request.method == "POST":
        form = signup_form(request.POST)
        if form.is_valid():
            opts = {}
            opts['use_https'] = request.is_secure()
            opts['token_generator'] = token_generator
            opts['email_template_name'] = email_template_name
            if not Site._meta.installed:
                opts['domain_override'] = RequestSite(request).domain
            form.save(**opts)
            return HttpResponseRedirect(post_signup_redirect)
    else:
        form = signup_form()
    return render_to_response(template_name, {'form': form, 'site_name':Site.objects.get_current().name, }, 
                              context_instance=RequestContext(request))

def signup_done(request, template_name='accounts/signup_done.html'):
    return render_to_response(template_name, 
                              context_instance=RequestContext(request))

def signup_confirm(request, uidb36=None, token=None,
                   token_generator=default_token_generator,
                   post_signup_redirect=None):
    assert uidb36 is not None and token is not None #checked par url
    if post_signup_redirect is None:
        post_signup_redirect = reverse('mywish.accounts.views.signup_complete')
    try:
        uid_int = base36_to_int(uidb36)
    except ValueError:
        raise Http404

    user = get_object_or_404(User, id=uid_int)
    context_instance = RequestContext(request)


    if token_generator.check_token(user, token):
        context_instance['validlink'] = True
        user.is_active = True
        user.save()
    else:
        context_instance['validlink'] = False

    t = loader.get_template('accounts/signup_complete_email.html')
    
    current_site = Site.objects.get_current()
    site_name = current_site.name
    domain = current_site.domain
            
    c = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'username': user.email,
        }
    
    email = EmailMessage("Welcome to %s" % site_name, 
                         t.render(Context(c)), 'service@fixsr.com',
                         [user.email], cc=['jzhao@yahoo.com'])
    
    email.content_subtype = "html"
    email.send()
    
    return HttpResponseRedirect(post_signup_redirect)

def signup_complete(request, template_name='accounts/signup_complete.html'):
    return render_to_response(template_name, 
                              context_instance=RequestContext(request, {'login_url': settings.LOGIN_URL}))