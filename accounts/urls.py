# In accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages

def web_register_view(request):
    """Handle web registration (session-based)"""
    if request.user.is_authenticated:
        return redirect('landing')
    
    if request.method == 'POST':
        from .forms import UserRegistrationForm
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # FIX: Set the backend attribute
            user.backend = 'accounts.backends.EmailBackend'
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('landing')
        else:
            return render(request, 'core/register.html', {'form': form})
    else:
        from .forms import UserRegistrationForm
        form = UserRegistrationForm()
    
    return render(request, 'core/register.html', {'form': form})


def web_profile_view(request):
    """Web profile page"""
    if not request.user.is_authenticated:
        return redirect('web-login')
    return render(request, 'accounts/profile.html', {'user': request.user})