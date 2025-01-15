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
import random
import string

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        action = request.POST.get('buton_register')
        action2 = request.POST.get('buton_login')
        if action2 == 'buton_login':
            username_login = request.POST['username_login']
            password_login = request.POST['password_login']
            user = authenticate(request, username=username_login, password=password_login)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('login:Test'))
            else:
                return render(request, 'login/login.html', {
                    'message': 'Invalid credentials.'
                })
        elif action == 'buton_register':
            username = request.POST.get('username')
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            email = request.POST.get('email')
            user_type = request.POST.get('user_type')
            first_name = request.POST.get('firstname')
            last_name = request.POST.get('lastname')
            if user_type == 'doctor':
                code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            else:
                code = '0000'
                
            #login conditions:
            if password != password_confirm:
                return render(request, 'login/login.html', {
                    'message': 'Passwords do not match.'})
            
            if User.objects.filter(username=username).exists():
                return render(request, 'login/login.html', {
                    'message': 'Username already exists.'})
            
            if User.objects.filter(email=email).exists():
                return render(request, 'login/login.html', {
                    'message': 'Email already exists.'})
            #email conditions
            if not re.search(r'@', email):
                return render(request, 'login/login.html', {
                    'message': 'Email not valid.'})
            
            #Password conditions

            if len(password) < 8:
                return render(request, 'login/login.html', {
                    'message': 'Password must be at least 8 characters long.'})
            
            if not re.search(r'\d', password):
                return render(request, 'login/login.html', {
                    'message': 'Password must contain at least one number.'})
            
            if not re.search(r'[.,!?/#]', password):
                return render(request, 'login/login.html', {
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
                user_profile = UserProfile(user=user, user_type=user_type, code=code, verification_token=verification_token)
                user_profile.save()
                login(request, user)

                # Send verification email
                """
                subject = 'Verify your email address'
                message = f'Please click the link to verify your email address: http://127.0.0.1:8000/users/verify-email/{verification_token}/'
                from_email = 'bardirobert1@gmail.com'
                recipient_list = [email]
                try:
                    send_mail(subject, message, from_email, recipient_list)
                except Exception as e:
                    return render(request, 'login/login.html', {'message': 'Error sending email: ' + str(e)})
                
                return render(request, 'login/login.html', {'message': 'Please check your email to verify your account.'})
                """
            except Exception as e:
                return render(request, 'login/login.html', {
                    'message': 'Error creating user: ' + str(e)
                })
                
        else:
            return render(request, 'login/login.html', {
                'message': 'Error creating user: ' + str(action) + ' ' + str(action2)
            })
    return render(request, 'login/login.html')


def logout_view(request):
    logout(request)
    return render(request, 'login/login.html', {
        'message': 'Logged out.'
    })

def dash_view(request):
    
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:login'))
    if request.method == 'POST':
        #form data
        resend = request.POST.get('email_resend')
        code = request.POST.get('code')
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
                return render(request, 'login/dash.html', {
                    'message': 'Passwords do not match.'})
            if len(password) < 8:
                return render(request, 'login/dash.html', {
                    'message': 'Password must be at least 8 characters long.'})
        
        #account updating
        try:
            user = request.user
            if code != "" and user.userprofile.user_type != 'doctor':
                user_profile = UserProfile.objects.get(user=user)
                user_profile.code = code
                user_profile.save()
            if username != "" and username != user.username:
                if User.objects.filter(username=username).exists():
                    return render(request, 'login/dash.html', {
                    'message': 'Username already exists.'})
                user.username = username
            if email != "" and email != user.email:
                if User.objects.filter(email=email).exists():
                    return render(request, 'login/dash.html', {
                    'message': 'Email already exists.'})
                user.email = email
            if first_name != "" and first_name != user.first_name:
                user.first_name = first_name
            if last_name != "" and last_name != user.last_name:
                user.last_name = last_name
            if password != "":
                user.set_password(password)
            user.save()
        except Exception as e:
            return render(request, 'login/dash.html', {
                'message': 'Error updating user: ' + str(e) + user.userprofile.user_type
            })
        # Send verification email
        if resend == "email_resend":
            verification_token = str(uuid.uuid4())
            user_profile = UserProfile.objects.get(user=user)
            user_profile.verification_token = verification_token
            user_profile.save()
            subject = 'Verify your email address'
            message = f'Please click the link to verify your email address: http://127.0.0.1:8000/users/verify-email/{verification_token}/'
            from_email = 'bardirobert1@gmail.com'
            recipient_list = [email]
            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                return render(request, 'login/dash.html', {'message': 'Error sending email: ' + str(e)})

            return render(request, 'login/dash.html', {'message': 'Please check your email to verify your account.'})
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        patient_code = user_profile.code
        doctor = UserProfile.objects.filter(user_type='doctor', code=patient_code).first()
        context = {
            'user_type': user_profile.user_type,
            'email_verified': user_profile.email_verified,
            'code': user_profile.code,
            'doctor': doctor,
            'message': request.GET.get('message', '')
        }
        return render(request, 'login/dash.html', context)    
    except:    
        return render(request, 'login/dash.html')
    
def verify_email(request,token):
    user_profile = get_object_or_404(UserProfile, verification_token=token)
    user_profile.email_verified = True
    user_profile.save()
    return HttpResponse('Email verified successfully. You can now log in.')
def Test(request):
    return render(request, "login/Test.html")