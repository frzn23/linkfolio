from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib import messages
from django.db import IntegrityError
from .models import Links

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        username = request.user.username
        insta = request.POST.get('instagram_url')
        linkedin = request.POST.get('linkedin_url')
        youtube = request.POST.get('youtube_url')
        website = request.POST.get('website_url')
        theme = request.POST.get('selected_theme')

        Links.objects.filter(username=username).update(insta_url=insta, linkedin_url=linkedin, youtube_url=youtube, website=website, theme=theme, link_status=True)
        messages.success(request, 'Links created successfully!')
        return redirect('index')
        # return render(request, 'dashboard.html')


    return render(request, 'dashboard.html')


def display(request):
        return render(request, 'display.html', {'theme':'img_2', 'instagram_url':'www.google.com', 'linkedin_url':'www.google.com', 'youtube_url':'www.google.com', 'website':'www.google.com'})


def login(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html', {'page_type': 'login'})

def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validate inputs
        if not username or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'login.html', {'page_type': 'signup'})
        
        # Check username length
        if len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters long.')
            return render(request, 'login.html', {'page_type': 'signup'})
            
        # Check password strength
        if len(password) < 4:
            messages.error(request, 'Password must be at least 4 characters long.')
            return render(request, 'login.html', {'page_type': 'signup'})
        
        try:
            # Create new user
            user = User.objects.create_user(
                username=username,
                password=password
            )
            
            # Log the user in
            auth_login(request, user)
            query = Links(username=username)
            query.save()
            messages.success(request, 'Account created successfully!')
            return redirect('index')
            
        except IntegrityError:
            messages.error(request, 'Username is already taken.')
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
    
    return render(request, 'login.html', {'page_type': 'signup'})

def logout(request):
    auth_logout(request)
    return redirect('login')