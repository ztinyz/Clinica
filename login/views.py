from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
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
            return render(request, 'login.html', {
                'message': 'Invalid credentials.'
            })
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return render(request, 'login.html', {
        'message': 'Logged out.'
    })

def register(request):
    if request.method == 'POST':
        #form data
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        password_confirm = request.POST.get('password_confirm')
        
        #login conditions:
        if password != password_confirm:
            return render(request, 'register.html', {
                'message': 'Passwords do not match.'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'message': 'Username already exists.'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'message': 'Email already exists.'})
        
        if len(password) < 8:
            return render(request, 'register.html', {
                'message': 'Password must be at least 8 characters long.'})
        
        #account creation
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('login:index'))
        except Exception as e:
            return render(request, 'register.html', {
                'message': 'Error creating user: ' + str(e)
            })
    return render(request, 'register.html')

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:login'))
    if request.method == 'POST':
        #form data
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        
        #login conditions:
        if password is not "":
            if password != password_confirm:
                return render(request, 'index.html', {
                    'message': 'Passwords do not match.'})
            if len(password) < 8:
                return render(request, 'index.html', {
                    'message': 'Password must be at least 8 characters long.'})
            
        if User.objects.filter(username=username).exists():
            return render(request, 'index.html', {
                'message': 'Username already exists.'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'index.html', {
                'message': 'Email already exists.'})
        

        #account updating
        try:
            user = request.user
            if username is not "":
                user.username = username
            if email is not "":
                user.email = email
            if first_name is not "":
                user.first_name = first_name
            if last_name is not "":
                user.last_name = last_name
            if password is not "":
                user.set_password(password)
            user.save()
        except Exception as e:
            return render(request, 'index.html', {
                'message': 'Error updating user: ' + str(e)
            })
    return render(request, 'index.html')

