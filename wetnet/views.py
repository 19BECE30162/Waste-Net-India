from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Get the form data
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            phone_number = form.cleaned_data.get('phone_number', '')
            address = form.cleaned_data.get('address', '')
            
            # Create the user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    phone_number=phone_number,
                    address=address
                )
                messages.success(request, 'Registration successful. You can now log in.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            # Form is not valid, show errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_phone = form.cleaned_data.get('username_or_phone')
            password = form.cleaned_data.get('password')
            
            # Try to authenticate with username first
            user = authenticate(username=username_or_phone, password=password)
            
            if user is None:
                # If username didn't work, try phone number
                users_with_phone = User.objects.filter(phone_number=username_or_phone)
                
                if users_with_phone.exists():
                    # Try to find a user with matching password
                    for potential_user in users_with_phone:
                        if potential_user.check_password(password):
                            user = authenticate(username=potential_user.username, password=password)
                            if user is not None:
                                break
            
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {user.username}.")
                return redirect('home')
            else:
                messages.error(request, "Invalid username/phone number or password.")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')

def home(request):
    return render(request, 'home.html')
