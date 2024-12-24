from django.shortcuts import render, redirect
from django.contrib.auth import login,logout, authenticate
from django.http import JsonResponse
import logging
from ...forms.CreateUserForm import CreateUserForm

tempUser = "uniqueID123"

def home(request):
    return render(request, "home.html")


def create_account(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            # Créer un nouveau compte pour l'utilisateur final
            form.save()
            return redirect('login')
    else:
        form = CreateUserForm()
    return render(request, 'Account/create_account.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'Account/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('home')


def logger(request):
    logger = logging.getLogger(__name__)
    logger.info("Message de log")
    return JsonResponse({"error": "Méthode non supportée."}, status=405)


