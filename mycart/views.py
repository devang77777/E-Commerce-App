from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from .forms import SignUpForm


def home(request):
    return render(request,'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('Home')
        else:
            error = "Invalid username or password"
            return render(request, 'login.html', {'error': error})
    return render(request, 'login.html')
# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             messages.success(request, "Login successful!")
#             return redirect("/")  # change 'home' to your landing page
#         else:
#             messages.error(request, "Invalid username or password")

#     return render(request, "login.html")


# def signup_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         email = request.POST.get("email")
#         password = request.POST.get("password")
#         confirm_password = request.POST.get("confirm_password")

#         if password != confirm_password:
#             messages.error(request, "Passwords do not match")
#             return redirect("signup")

#         if User.objects.filter(username=username).exists():
#             messages.error(request, "Username already taken")
#             return redirect("signup")

#         user = User.objects.create_user(username=username, email=email, password=password)
#         user.save()
#         messages.success(request, "Account created successfully! Please log in.")
#         return redirect("login")

#     return render(request, "signup.html")

@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        # Debug: Print CSRF token info
        print(f"CSRF Token in request: {request.POST.get('csrfmiddlewaretoken', 'NOT FOUND')}")
        print(f"CSRF Token in session: {request.session.get('csrf_token', 'NOT FOUND')}")
        
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            welcome_name = user.first_name if user.first_name else user.username
            messages.success(request, f'Welcome {welcome_name}! Your account has been created successfully.')
            return redirect('Home')  # Redirect to shop homepage
        else:
            messages.error(request, 'Please correct the errors below.')
            # Debug: Print form errors
            print(f"Form errors: {form.errors}")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('Home')