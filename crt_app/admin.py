from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models.academic import *
from .models.attendance import Attendance
from .models.performance import Performance
from crt_app.utils.logger import log_info, log_error


@admin.register(Users)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'email')

    def save_model(self, request, obj, form, change):
        log_info(f"User modified: {obj.username}")
        super().save_model(request, obj, form, change)

@admin.register(TPOProfile)
class TPOAdmin(admin.ModelAdmin):

    exclude = ('user',)

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            user = Users.objects.create(
                username=obj.tpo_name,
                email=obj.tpo_email,
                role='TPO',
                password=make_password('sober')
            )
            obj.user = user

        super().save_model(request, obj, form, change)

@admin.register(StudentProfile)
class StudentAdmin(admin.ModelAdmin):

    exclude = ('user', 'tpo')

    def save_model(self, request, obj, form, change):
        if not (obj.user_id or obj.tpo):
            user = Users.objects.create(
                username=obj.stu_name,
                email=obj.stu_email,
                role='STUDENT',
                password=make_password(obj.rtu_roll_no)
            )
            tpo =TPOProfile.objects.get(tpo_email = obj.tpo_email)
            obj.tpo = tpo
            obj.user = user

        super().save_model(request, obj, form, change)


@admin.register(InstructorProfile)
class InstructorAdmin(admin.ModelAdmin):

    exclude = ('user',)

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            user = Users.objects.create(
                username=obj.ins_name,
                email=obj.ins_email,
                role='INSTRUCTOR',
                password=make_password('sober')
            )
            obj.user = user

        super().save_model(request, obj, form, change)

@admin.register(InterviewerProfile)
class InterviewerAdmin(admin.ModelAdmin):

    exclude = ('user',)

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            user = Users.objects.create(
                username=obj.int_name,
                email=obj.int_email,
                role='TPO',
                password=make_password('sober')
            )
            obj.user = user

        super().save_model(request, obj, form, change)

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):

    exclude = ('student', 'interviewer')

    def save_model(self, request, obj, form, change):
        if not (obj.student or obj.interviewer):
            student = StudentProfile.objects.get(
                stu_name=obj.stu_name,
                stu_email=obj.stu_email,
            )
            interviewer = InterviewerProfile.objects.get(
                int_email = obj.int_email
            )
            obj.student = student
            obj.interviewer = interviewer

        super().save_model(request, obj, form, change)


@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    exclude = ('instructor',)

    def save_model(self, request, obj, form, change):
        if not obj.instructor:
            instructor = InstructorProfile.objects.get(
                ins_email = obj.ins_email
            )
            obj.instructor = instructor

        super().save_model(request, obj, form, change)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    exclude = ('student', 'class_obj')

    def save_model(self, request, obj, form, change):
        if not (obj.student or obj.class_obj):
            student = StudentProfile.objects.get(
                stu_name=obj.stu_name,
                stu_email=obj.stu_email,
            )
            class_ = Classes.objects.get(class_name = obj.class_name, 
                                        date = obj.date, 
                                        start_time = obj.start_time, 
                                        end_time = obj.end_time, 
                                        venue = obj.venue)
            obj.student = student
            obj.class_obj = class_

        super().save_model(request, obj, form, change)


