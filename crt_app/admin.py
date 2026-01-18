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

    exclude = ('user',)

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            user = Users.objects.create(
                username=obj.stu_name,
                email=obj.stu_email,
                role='STUDENT',
                password=make_password(obj.rtu_roll_no)
            )
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

admin.site.register(Classes)
admin.site.register(Attendance)
admin.site.register(Performance)

