from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages

from .forms import CustomUserCreationForm
from BEcom.tasks import send_welcome_email_task


class SignUpView(CreateView):
    form_class = CustomUserCreationForm  # <-- use your custom form here
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home") 
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})  

def password_reset(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("password_reset_done")
    else:
        form = PasswordResetForm()
    return render(request, "registration/password_reset_form.html", {"form": form})

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_welcome_email_task.delay(user.id) # Pass the new user's ID
            messages.success(request, 'Registration successful! Please check your email for a welcome message.')
            login(request, user)
            return redirect("home") 
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request):
    return render(request, "registration/profile.html", {"user": request.user})

@login_required
def account_settings(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account settings updated successfully.')
            return redirect("profile")
    else:
        form = CustomUserCreationForm(instance=request.user)
    return render(request, "registration/account_settings.html", {"form": form})

@login_required
def profile_edit(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect("profile")
    else:
        form = CustomUserCreationForm(instance=request.user)
    return render(request, "registration/profile_edit.html", {"form": form})
@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect("home")
    return render(request, "registration/delete_account.html", {"user": request.user})