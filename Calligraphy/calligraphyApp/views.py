from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import *
from .forms import *
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib import messages  
from django.contrib.auth import authenticate, login as auth_login  
import logging  



#
#def login(request):  
#    if request.method == 'POST':  
#        form = AuthenticationForm(data=request.POST)  
#        if form.is_valid():  
#            username = form.cleaned_data.get('username')  
#            password = form.cleaned_data.get('password')  
#            user = authenticate(username=username, password=password)  
#            if user is not None:  
#                auth_login(request, user)  
#                return redirect('home')  
#            else:  
#                messages.error(request, "Invalid username or password.")    
#        else:  
#            messages.error(request, "There was a problem with your submission.")  
#    else:  
#        form = AuthenticationForm()  
#    return render(request, 'calligraphyApp/registration/login.html', {'form': form})  
#
def user_login(request):
    logger = logging.getLogger(__name__)  # Set up logging  
    if request.method == "POST":  
        form = LoginForm(request.POST)  
        if form.is_valid():  
            cd = form.cleaned_data  
            user = authenticate(username=cd['username'], password=cd['password'])  
            if user is not None:  
                if user.is_active:  
                    auth_login(request, user)  # Log the user in  
                    return redirect('home')  # Redirect to home after successful login  
                else: 
                    logger.warning(f"User {cd['username']} tried to log in but is inactive.")  
                    messages.error(request, "Your account is disabled.")  
            else:
                logger.warning(f"Failed login attempt for {cd['username']}.")  
                messages.error(request, "Invalid username or password.")  
    else:  
        form = LoginForm()  
    
    return render(request, 'calligraphyApp/registration/login.html', {'form': form})  


#def register(request):  
#    if request.method == 'POST':  
#        form = UserRegistrationForm(request.POST)  
#        if form.is_valid():  
#            form.save()  # Save the new user  
#            username = form.cleaned_data.get('username')  
#            messages.success(request, f'Your account has been created! You can now log in.')  
#            return redirect('login')  # Redirect to the login page after successful registration  
#    else:  
#        form = UserRegistrationForm()  
#    return render(request, 'calligraphyApp/registration/register.html', {'form': form})  


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'calligraphyApp/registration/register.html', {'form': form})


def home(request):  
    courses = Course.objects.all()  # Fetching all courses  
    return render(request, 'calligraphyApp/home.html', {'courses': courses})  



def part_detail(request, part_id):  
    part = get_object_or_404(Part, id=part_id)  
    # Only show videos to authenticated users  
    videos = part.videos.all() if request.user.is_authenticated else []  
    return render(request, 'calligraphyApp/part_detail.html', {'part': part, 'videos': videos})  



@login_required  # Only allow logged-in users to access this view  
def user_list(request):  
    users = User.objects.all()  # Get all registered users  
    return render(request, 'calligraphyApp/user_list.html', {'users': users})  

def profile_view(request):  
    # Display user profile (not fully implemented here)  
    return render(request, 'profile.html')  