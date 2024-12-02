from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Q
import logging
# from django.core.files.storage import FileSystemStorage
from .models.FinalUser import FinalUser
from .models.SoundBoard import SoundBoard
from .forms.SoundBoardForm import SoundBoardForm
from .filters.SoundBoardFilter import SoundBoardFilter

tempUser = "uniqueID123"

def home(request):
    # if request.method == "POST" and request.FILES["image_file"]:
    #     image_file = request.FILES["image_file"]
    #     fs = FileSystemStorage()
    #     filename = fs.save(image_file.name, image_file)
    #     image_url = fs.url(filename)
    #     print(image_url)
    #     return render(request, "home.html", {
    #         "image_url": image_url
    #     })
    return render(request, "home.html")


#CRUD SoundBoard
def soundboard_list(request):
    _query_Set = SoundBoard.objects.all().order_by('id')
    _filter = SoundBoardFilter(queryset=_query_Set)
    soundboards = _filter.filter_by_user_id(tempUser)
    
    return render(request, 'soundboard_list.html', {'soundboards': soundboards})


def soundboard_create(request):
    if request.method == 'POST':
        form = SoundBoardForm(request.POST)
        if form.is_valid():
            soundboard = form.save(commit=False)
            soundboard.finalUser = FinalUser.objects.get(userID=tempUser)
            soundboard.save()
            return redirect('soundboardsList')
    else:
        form = SoundBoardForm()
    return render(request, 'soundboard_form.html', {'form': form })


def soundboard_read(request, soundboard_id):
    soundboard = SoundBoard.objects.get(id=soundboard_id)
    if not soundboard or soundboard.finalUser.userID != tempUser:
        return render(request, '404.html', status=404)
    else:   
        return render(request, 'soundboard_read.html', {'soundboard': soundboard})

def soundboard_update(request, soundboard_id):
    soundboard = SoundBoard.objects.get(id=soundboard_id)
    if request.method == 'POST':
        if not soundboard or soundboard.finalUser.userID != tempUser:
            return render(request, '404.html', status=404)
        else:
            form = SoundBoardForm(request.POST, instance=soundboard)
            if form.is_valid():
                form.save()
                return redirect('soundboardsList')
    else:
        if not soundboard or soundboard.finalUser.userID != tempUser:
            return render(request, '404.html', status=404) 
        else:
            form = SoundBoardForm(instance=soundboard)
    return render(request, 'soundboard_form.html', {'form': form})

def soundboard_delete(request, soundboard_id) -> JsonResponse:
    soundboard = SoundBoard.objects.get(id=soundboard_id)
    if request.method == 'POST':
        if not soundboard or soundboard.finalUser.userID != tempUser:
            return JsonResponse({"error": "SoundBoard introuvable."}, status=404)
        else :
            soundboard.delete()
            return JsonResponse({'success': 'Suppression réussie'}, status=200)
    return JsonResponse({"error": "Méthode non supportée."}, status=405)





def logger(request):
    logger = logging.getLogger(__name__)
    logger.info("Message de log")
    return JsonResponse({"error": "Méthode non supportée."}, status=405)


def final_user_view(request):
    # Créer un utilisateur si une méthode POST est utilisée
    if request.method == "POST":
        email = request.POST.get("email")
        user_id = request.POST.get("userID")
        
        if email and user_id:
            final_user = FinalUser.objects.create(email=email, userID=user_id)
            return JsonResponse({
                "message": "Utilisateur créé avec succès.",
                "id": str(final_user.id),
                "email": final_user.email,
                "userID": final_user.userID
            }, status=201)
        return JsonResponse({"error": "Email et userID sont requis."}, status=400)

    # Récupérer la liste de tous les utilisateurs
    elif request.method == "GET":
        users = FinalUser.objects.all().values("id", "email", "userID")
        return JsonResponse(list(users), safe=False, status=200)
    
    return JsonResponse({"error": "Méthode non supportée."}, status=405)
