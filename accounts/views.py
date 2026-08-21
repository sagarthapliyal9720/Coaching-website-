# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import User

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        role = request.POST.get('role')
        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        class_level = request.POST.get('class_level')
        batch = request.POST.get('batch')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Basic validations
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken!")
            return render(request, 'accounts/register.html')

        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number is already registered!")
            return render(request, 'accounts/register.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            phone_number=phone_number,
            role=role,
            class_level=class_level,
            batch=batch
        )
        
        login(request, user)
        messages.success(request, f"Welcome {user.full_name}! Registration successful.")
        return redirect('home')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')