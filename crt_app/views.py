from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from crt_app.services.user_services import UserService
from crt_app.services.classes_services import ClassServices
from crt_app.services.performance_services import PerformanceServices
from crt_app.services.attendance_services import AttendanceServices
import json
from crt_app.utils.logger import log_error, log_info

@csrf_exempt
def create_instructor(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        log_info(f"Attempting to create instructor -> {data['tpo_email']}")
        instructor = UserService.create_instructor(data=data)
        
        return JsonResponse({
            "message": "Instructor created",
            "id": str(instructor.user.id),
            "name": instructor.full_name
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
def create_student(request):
    if request.method != "POST":
        return JsonResponse({"error" : "Only POST allowed"}, status = 405)
    
    try:
        data = json.loads(request.body)
        log_info(f"Attempting to create student -> {data['stu_email']}")
        student = UserService.create_student(data=data)
        return JsonResponse({
            "message" : "Student created",
            "id" : str(student.student.id)
        })
    except Exception as e:
        return JsonResponse({"error" : str(e)}, status=500)
    

@csrf_exempt
def create_tpo(request):
    if request.method != "POST":
        return JsonResponse({"error" : "Only POST allowed"}, status = 405)
    try:
        data = json.loads(request.body)
        tpo = UserService.create_tpo(data=data)
        return JsonResponse({
            "message" : "tpo created",
            "id" : str(tpo.user.id)
        })
    except Exception as e:
        return JsonResponse({"error" : str(e)}, status=500)
    
@csrf_exempt
def create_interviewer(request):
    if request.method != "POST":
        return JsonResponse({"error" : "Only POST allowed"}, status = 405)
    try:
        data = json.loads(request.body)
        interviewer = UserService.create_interviewer(data=data)
        return JsonResponse({
            "message" : "interviewer created",
            "id" : str(interviewer.user.id)
        })
    except Exception as e:
        return JsonResponse({"error" : str(e)}, status=500)
    
@csrf_exempt
def create_class(request):
    if request.method != "POST":
        return JsonResponse({"error" : "Only POST allowed"}, status = 405)
    try:
        data = json.loads(request.body)
        created_class = ClassServices.create_class(data=data)
        return JsonResponse({
            "message" : "interviewer created",
            "id" : str(created_class.id)
        })
    except Exception as e:
        return JsonResponse({"error" : str(e)}, status=500)
    
@csrf_exempt
def create_performance(request):
    if request.method != "POST":
        return JsonResponse({"error" : "Only POST allowed"}, status = 405)
    try:
        data = json.loads(request.body)
        performance = PerformanceServices.create_class(data=data)
        return JsonResponse({
            "message" : "performance created",
            "id" : str(performance.id)
        })
    except Exception as e:
        return JsonResponse({"error" : str(e)}, status=500)
    
@csrf_exempt
def create_attendance(request):
    if request.method != "POST":
        return JsonResponse({"error" : "Only POST allowed"}, status = 405)
    try:
        data = json.loads(request.body)
        attendance = AttendanceServices.create_attendance(data=data)
        return JsonResponse({
            "message" : "attendance created",
            "id" : str(attendance.id)
        })
    except Exception as e:
        return JsonResponse({"error" : str(e)}, status=500)