from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib import messages
from django.db import IntegrityError
from .models import Links, LinkClick
from django.db.models import Count
from django.http import HttpResponse
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.serializers.json import DjangoJSONEncoder
import json



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

    q = Links.objects.filter(username=request.user.username).values()[0]
    username = request.user.username
    return render(request, 'dashboard.html', {'username': username,'data':q})


def display(request, username):
        user_id = username
        data = Links.objects.get(username=user_id)
        if data.link_status == False:
            return HttpResponse('<h1>Link Is Inactive as there is no urls. Please set up the link. <a href="/">Go Back</a></h1>')
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
    
    # Get daily clicks with link type breakdown
    daily_clicks = LinkClick.objects.filter(
        username=username,
        clicked_at__gte=start_date
    ).annotate(
        date=TruncDate('clicked_at')
    ).values('date', 'link_type').annotate(
        total=Count('id')
    ).order_by('date')

    # Restructure the data to group by date with counts for each link type
    daily_clicks_formatted = {}
    for click in daily_clicks:
        date = click['date'].strftime('%Y-%m-%d') if isinstance(click['date'], datetime) else click['date']
        
        if date not in daily_clicks_formatted:
            daily_clicks_formatted[date] = {
                'date': date,
                'website': 0,
                'linkedin': 0,
                'instagram': 0,
                'youtube': 0
            }
        
        link_type = click['link_type']
        if link_type in daily_clicks_formatted[date]:
            daily_clicks_formatted[date][link_type] = click['total']

    # Convert to list for the template
    daily_clicks_list = list(daily_clicks_formatted.values())
    
    # Get clicks by type
    clicks_by_type = list(LinkClick.objects.filter(
        username=username
    ).values('link_type').annotate(
        total=Count('id')
    ).order_by('-total'))  # Sort by most clicks
    
    # Get total clicks
    total_clicks = LinkClick.objects.filter(username=username).count()
    
    # Get recent clicks (last 24 hours)
    recent_clicks = LinkClick.objects.filter(
        username=username,
        clicked_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    # Add recent clicks to context
    context = {
        'daily_clicks_json': json.dumps(daily_clicks_list, cls=DjangoJSONEncoder),
        'clicks_by_type_json': json.dumps(clicks_by_type, cls=DjangoJSONEncoder),
        'total_clicks': total_clicks,
        'recent_clicks': recent_clicks,
    }
    
    return render(request, 'analytics.html', context)


def track_click(request, username, link_type):
    # Simply create a click record
    LinkClick.objects.create(
        username=username,
        link_type=link_type
    )
    
    # Get the redirect URL from Links model
    user_links = Links.objects.get(username=username)
    
    # Get the appropriate URL based on link type
    redirect_url = {
        'website': user_links.website,
        'instagram': user_links.insta_url,
        'linkedin': user_links.linkedin_url,
        'youtube': user_links.youtube_url
    }.get(link_type)
    
    # Redirect to the URL
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