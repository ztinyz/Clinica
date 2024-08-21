from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:login'))
    return render(request, 'index.html')

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


