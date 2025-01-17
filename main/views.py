from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib import messages
from django.db import IntegrityError
from .models import Links, LinkClick
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime


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


def display(request, username):
        user_id = username
        data = Links.objects.get(username=user_id)
        theme = data.theme
        insta = data.insta_url
        linkedin = data.linkedin_url
        yt = data.youtube_url
        web = data.website
        
        link = {
        'username': user_id,
        'website': web,
        'instagram_url': insta,
        'linkedin_url': linkedin,
        'youtube_url': yt,
        'theme': theme
        }

        params = {'theme':theme, 'instagram_url':insta, 'linkedin_url':linkedin, 'youtube_url':yt, 'website':web}
        return render(request, 'display.html', {'link':link})

def analytics(request):
    if not request.user.is_authenticated:
        return redirect('login')        
    username = request.user.username
    
    # Get date range (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get daily clicks
    daily_clicks = LinkClick.objects.filter(
        username=username,
        clicked_at__gte=start_date
    ).annotate(
        date=TruncDate('clicked_at')
    ).values('date').annotate(
        total=Count('id')
    ).order_by('date')

    # Convert date objects to strings
    daily_clicks = [
        {'date': daily_click['date'].strftime('%Y-%m-%d'), 'total': daily_click['total']}
        for daily_click in daily_clicks
    ]
    
    # Get clicks by link type
    clicks_by_type = LinkClick.objects.filter(
        username=username
    ).values('link_type').annotate(
        total=Count('id')
    )
    
    # Get total clicks
    total_clicks = LinkClick.objects.filter(username=username).count()
    
    context = {
        'daily_clicks': daily_clicks,
        'clicks_by_type': list(clicks_by_type),  # Ensure it's JSON serializable
        'total_clicks': total_clicks,
    }
    
    return render(request, 'analytics.html', context)


def track_click(request, username, link_type):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    LinkClick.objects.create(
        username=username,
        link_type=link_type,
        visitor_ip=ip
    )
    
    # Get the redirect URL from Links model
    user_links = Links.objects.get(username=username)
    if link_type == 'website':
        redirect_url = user_links.website
    elif link_type == 'instagram':
        redirect_url = user_links.insta_url
    elif link_type == 'linkedin':
        redirect_url = user_links.linkedin_url
    elif link_type == 'youtube':
        redirect_url = user_links.youtube_url
    
    return redirect(redirect_url)


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