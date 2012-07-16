from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import int_to_base36
from django.template import Context, loader
from django import forms
from django.core.mail import EmailMessage
from mywish.models import UserProfile
import datetime, random, hashlib, mywish.settings
import mywish.utils
import base64, time
from django.db import transaction
from django.contrib.auth import login, get_backends
from django.contrib.auth import authenticate

class MyUser(User):
    class Meta:
        proxy = True

    def __unicode__(self):
        return u"%s - %s" % (self.username, self.email)

class UserLoginForm(forms.Form):
    username= forms.CharField(label='Username/Email',max_length=30)
    password= forms.CharField(label='Password', widget=forms.PasswordInput())
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError("Your username or password is incorrect.")
            elif not self.user.is_active:
                raise forms.ValidationError("Your account is inactive.")

        return self.cleaned_data

    def get_user(self):
        return self.user
    
class LoginAsForm(forms.Form):
    """
    Sometimes to debug an error you need to login as a specific User.
    This form allows you to log as any user in the system. You can restrict
    the allowed users by passing a User queryset paramter, `qs` when the
    form is instantiated.
    """
    user = forms.ModelChoiceField(MyUser.objects.all())
    
    def __init__(self, data=None, files=None, request=None, qs=None, *args,
                 **kwargs):
        if request is None:
            raise TypeError("Keyword argument 'request' must be supplied")                 
        super(LoginAsForm, self).__init__(data=data, files=files, *args, **kwargs)
        self.request = request
        if qs is not None:
            self.fields["user"].queryset = qs


    def save(self):
        user = self.cleaned_data["user"]

        # In lieu of a call to authenticate()
        backend = get_backends()[0]
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        login(self.request, user)
        
        message = "Logged in as %s" % self.request.user        
        self.request.user.message_set.create(message=message)
        
class UserCreationForm(forms.ModelForm):
#    username = forms.RegexField(label="Username", max_length=30, regex=r'^[\w.@+-]+$',
#                                help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
#                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
#    first = forms.RegexField(label="First name", max_length=30, regex=r'^[\w\s.@+-]+$',
#                                help_text="Required. 30 characters or fewer. ",
#                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})
#    last = forms.RegexField(label="Last name", max_length=30, regex=r'^[\w\s.@+-]+$',
#                                help_text="Required. 30 characters or fewer. ",
#                                error_messages = {'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters."})

    password1 = forms.CharField(label="Password", max_length=30, widget=forms.PasswordInput)
#    password2 = forms.CharField(label="Password confirmation", max_length=30, widget=forms.PasswordInput,
#                                help_text = "Enter the same password as above, for verification.")
    email1 = forms.EmailField(label="Email", max_length=75)
#    phone = forms.CharField(label="Phone", max_length=25, required=False)

    #add this as a short term solution
    #invitation = forms.CharField(label="Invitation Code", max_length=30)

#    email2 = forms.EmailField(label="Email confirmation", max_length=75,
#                              help_text = "Enter your email address again. A confirmation email will be sent to this address.")

    #company_name = forms.CharField(label='Company Name',max_length=50)
    #website_url = forms.CharField(label='Website URL',max_length=50)
    #website_url="http://"
    
    class Meta:
        model = User
        fields = ("email1",)

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1", "")

        if str(password1).__len__() < 6:
            raise forms.ValidationError("Minimum 6 characters.")
        return password1
    
#    def clean_password2(self):
#        password1 = self.cleaned_data.get("password1", "")
#        password2 = self.cleaned_data["password2"]
#        if password1 != password2:
#            raise forms.ValidationError("The two password fields didn't match.")
#        return password2
    
    def clean_email1(self):
        email1 = self.cleaned_data["email1"]
        users_found = User.objects.filter(email__iexact=email1)
        if len(users_found) >= 1:
            raise forms.ValidationError("A user with that email already exist.")
        return email1

#    def clean_invitation(self):
#        invitation = self.cleaned_data["invitation"]
#        if invitation != 'bttextbayg' and invitation !='2011trysg' and invitation!='2011tTrack':
#            raise forms.ValidationError("Invalid invitation code.")
#        return invitation
    
#    def clean_email2(self):
#        email1 = self.cleaned_data.get("email1", "")
#        email2 = self.cleaned_data["email2"]
#        if email1 != email2:
#            raise forms.ValidationError("The two email fields didn't match.")
#        return email2

#    def clean_company_name(self):
#        company_name = self.cleaned_data["company_name"]
#        company_found = Company.objects.filter(name__iexact=company_name)
#        if len(company_found) >= 1:
#            raise forms.ValidationError("A company with that email already exist.")
#        return company_name
#
#    def clean_website_url(self):
#        website_url = self.cleaned_data["website_url"]
#        website_found = Website.objects.filter(url__iexact=website_url)
#        if len(website_found) >= 1:
#            raise forms.ValidationError("A website with that URL already exist.")
#        return website_url

    def save(self, commit=True, domain_override=None,
             email_template_name='accounts/signup_email.html',
             use_https=False, token_generator=default_token_generator):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email1"]
#        user.first_name = self.cleaned_data["first"]
#        user.last_name = self.cleaned_data["last"]
        user.username = user.email
        user.is_active = False

        if commit:
            user.save()
            
            userProfile = UserProfile()
            s = hashlib.sha1()
            s.update(str(random.random()))
            salt = s.hexdigest()[:5]

            #userProfile.activation_key = sha.new(salt+user.username).hexdigest()
            userProfile.activiation_key = token_generator.make_token(user)
            userProfile.key_expires = datetime.datetime.today() + datetime.timedelta(days=2)
            #userProfile.invitation_code = self.cleaned_data["invitation"]
            userProfile.user = user

            userProfile.save()
                                    
        if not domain_override:
            current_site = Site.objects.get_current()
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
            
        t = loader.get_template(email_template_name)
        c = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': int_to_base36(user.id),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': 'http',
            }
        
        email = EmailMessage("Activate Your %s Account" % site_name, 
                             t.render(Context(c)), 'service@fixsr.com',
                             [user.email], cc=['service@fixsr.com'])
        email.content_subtype = "html"
        email.send()
        
        return user
