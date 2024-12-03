from django.shortcuts import render, redirect
from django.http import JsonResponse
import logging
from ...models.FinalUser import FinalUser

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
