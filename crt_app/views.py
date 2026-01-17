from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from crt_app.services.user_services import UserService
import json

@csrf_exempt
def create_instructor(request):

    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    data = json.loads(request.body)

    instructor = UserService.create_instructor(
        name=data.get("name"),
        email=data.get("email")
    )

    return JsonResponse({
        "message": "Instructor created",
        "id": str(instructor.id),
        "name": instructor.full_name
    })
