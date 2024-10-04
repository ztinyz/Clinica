from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from .models import UserProfile
import re
import uuid
# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('login:index'))
        else:
            return render(request, 'login/login.html', {
                'message': 'Invalid credentials.'
            })
    return render(request, 'login/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'login/login.html', {
        'message': 'Logged out.'
    })

def verify_email(request,token):
    user_profile = get_object_or_404(UserProfile, verification_token=token)
    user_profile.email_verified = True
    user_profile.save()
    return HttpResponse('Email verified successfully. You can now log in.')


def register(request):
    if request.method == 'POST':
        #form data
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        #login conditions:
        if password != password_confirm:
            return render(request, 'login/register.html', {
                'message': 'Passwords do not match.'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'login/register.html', {
                'message': 'Username already exists.'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'login/register.html', {
                'message': 'Email already exists.'})
        #email conditions
        if not re.search(r'@', email):
            return render(request, 'login/register.html', {
                'message': 'Email not valid.'})
        
        #Password conditions

        if len(password) < 8:
            return render(request, 'login/register.html', {
                'message': 'Password must be at least 8 characters long.'})
        
        if not re.search(r'\d', password):
            return render(request, 'login/register.html', {
                'message': 'Password must contain at least one number.'})
        
        if not re.search(r'[.,!?/#]', password):
            return render(request, 'login/register.html', {
                'message': 'Password must contain at least one special character(.,!?/#).'})
        
        #account creation
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            user.save()
            verification_token = str(uuid.uuid4())
            user_profile = UserProfile(user=user, user_type=user_type, verification_token=verification_token)
            user_profile.save()
            login(request, user)

            # Send verification email
            subject = 'Verify your email address'
            message = f'Please click the link to verify your email address: http://127.0.0.1:8000/users/verify-email/{verification_token}/'
            from_email = 'bardirobert1@gmail.com'
            recipient_list = [email]
            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                return render(request, 'login/register.html', {'message': 'Error sending email: ' + str(e)})

            return render(request, 'login/register.html', {'message': 'Please check your email to verify your account.'})
        except Exception as e:
            return render(request, 'login/register.html', {
                'message': 'Error creating user: ' + str(e)
            })
    return render(request, 'login/register.html')

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:login'))
    if request.method == 'POST':
        #form data
        username = request.POST.get('username')
        Logout = request.POST.get('Logout')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        if Logout:
            return HttpResponseRedirect(reverse('login:logout'))
        #login conditions:
        if password != "":
            if password != password_confirm:
                return render(request, 'login/index.html', {
                    'message': 'Passwords do not match.'})
            if len(password) < 8:
                return render(request, 'login/index.html', {
                    'message': 'Password must be at least 8 characters long.'})
            
        if User.objects.filter(username=username).exists():
            return render(request, 'login/index.html', {
                'message': 'Username already exists.'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'login/index.html', {
                'message': 'Email already exists.'})
        
        #account updating
        try:
            user = request.user
            if username != "":
                user.username = username
            if email != "":
                user.email = email
            if first_name != "":
                user.first_name = first_name
            if last_name != "":
                user.last_name = last_name
            if password != "":
                user.set_password(password)
            user.save()
        except Exception as e:
            return render(request, 'login/index.html', {
                'message': 'Error updating user: ' + str(e)
            })
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        context = {
            'user_type': user_profile.user_type,
            'email_verified': user_profile.email_verified,
            'message': request.GET.get('message', '')
        }
        return render(request, 'login/index.html', context)    
    except:    
        return render(request, 'login/index.html')

def reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not User.objects.filter(email=email).exists():
            return render(request, 'login/reset.html', {
                'message': 'Email does not exist.'
            })
        user = User.objects.get(email=email)
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()
        subject = 'Password Reset'
        message = 'Your new password is: ' + new_password
        from_email = 'bardirobert1@gmail.com'
        recipient_list = [email]
        try:
            send_mail(subject, message, from_email, recipient_list)
            return render(request, 'login/login.html', {'message': 'Please check your email for your temporary password.'})
        except Exception as e:
            return render(request, 'login/password_reset.html', {'message': 'Error sending email: ' + str(e)})
    return render(request, 'login/password_reset.html')

