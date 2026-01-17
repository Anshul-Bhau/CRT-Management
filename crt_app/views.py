from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from crt_app.services.user_services import UserService
import json

@csrf_exempt
def create_instructor(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        instructor = UserService.create_instructor(data=data)
        return JsonResponse({
            "message": "Instructor created",
            "id": str(instructor.id),
            "name": instructor.full_name
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    