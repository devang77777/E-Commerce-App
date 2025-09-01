from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login


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

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Change 'home' to your homepage url name
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})