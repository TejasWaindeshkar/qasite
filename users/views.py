# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm, UserProfileForm
from .models import UserProfile


# ─────────────────────────────────────────
# REGISTER VIEW
# ─────────────────────────────────────────
def register_view(request):
    # if already logged in, go home
    if request.user.is_authenticated:
        return redirect('question_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # auto-create UserProfile for new user
            UserProfile.objects.create(user=user)

            # log them in immediately after register
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account is created.")
            return redirect('question_list')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


# ─────────────────────────────────────────
# LOGIN VIEW
# ─────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('question_list')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")

            # redirect to the page they were trying to visit
            next_url = request.GET.get('next', 'question_list')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


# ─────────────────────────────────────────
# LOGOUT VIEW
# ─────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ─────────────────────────────────────────
# PROFILE VIEW
# ─────────────────────────────────────────
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile      = get_object_or_404(UserProfile, user=profile_user)
    questions    = profile_user.questions.all()[:10]
    answers      = profile_user.answers.all()[:10]

    return render(request, 'users/profile.html', {
        'profile_user': profile_user,
        'profile'     : profile,
        'questions'   : questions,
        'answers'     : answers,
    })


# ─────────────────────────────────────────
# EDIT PROFILE VIEW
# ─────────────────────────────────────────
@login_required
def edit_profile_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'users/edit_profile.html', {'form': form})