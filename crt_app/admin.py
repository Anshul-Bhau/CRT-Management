from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import *
from import_export.admin import ImportExportModelAdmin, ExportMixin
from crt_app.utils.logger import log_info, log_error
from django.db import transaction
from .resources import *

@admin.register(Users)
class UserAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = UserResource
    list_display = ('username', 'role', 'email')

    def save_model(self, request, obj, form, change):
        log_info(f"User modified: {obj.username}")
        super().save_model(request, obj, form, change)

@admin.register(TPOProfile)
class TPOAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = TPOResource
    list_display = ('tpo_name', 'tpo_email')
    exclude = ('user',)

    @transaction.atomic
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
class StudentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = StudentResource
    list_display = ('stu_name', 'stu_email', 'rtu_roll_no', 'branch', 'tpo_email', 'attendance')
    exclude = ('user', 'tpo')

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if not (obj.user_id or obj.tpo):
            user = Users.objects.create(
                username=obj.stu_name,
                email=obj.stu_email,
                role='STUDENT',
                password=make_password(obj.rtu_roll_no)
            )
            try:
                tpo = TPOProfile.objects.get(
                    tpo_email=obj.tpo_email
                )
            except TPOProfile.DoesNotExist:
                raise ValueError(
                    f"TPO not found → {obj.tpo_email}"
                )
            obj.tpo = tpo
            obj.user = user

        super().save_model(request, obj, form, change)


@admin.register(InstructorProfile)
class InstructorAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = InstructorResource
    list_display = ('ins_name', 'ins_email')
    exclude = ('user',)

    @transaction.atomic
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
class InterviewerAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class =  InterviewerResource
    list_display = ('int_name', 'int_email', 'sub')
    exclude = ('user',)

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            user = Users.objects.create(
                username=obj.int_name,
                email=obj.int_email,
                role='INTERVIEWER',
                password=make_password('sober')
            )
            obj.user = user

        super().save_model(request, obj, form, change)

@admin.register(Performance)
class PerformanceAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = PerformanceExportResource
    list_display = ('stu_name', 'stu_email', 'subject', 'date')
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
class ClassesAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = ClassesResource
    list_display = ('class_name', 'date', 'venue', 'start_time', 'end_time')
    exclude = ('instructor',)

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        if not obj.instructor:
            instructor = InstructorProfile.objects.get(
                ins_email = obj.ins_email
            )
            obj.instructor = instructor

        super().save_model(request, obj, form, change)

@admin.register(Attendance)
class AttendanceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = AttendanceResource
    list_display = ('stu_email', 'class_name', 'date', 'venue', 'attended')
    exclude = ('student', 'class_obj')

    def save_model(self, request, obj, form, change):
        if not obj.student_id:
            try:
                obj.student = StudentProfile.objects.get(
                    stu_email=obj.stu_email
                )
            except StudentProfile.DoesNotExist:
                raise ValidationError(
                    f"No student found with email {obj.stu_email}"
                )

    
        if not obj.class_obj_id:
            class_qs = Classes.objects.filter(
                class_name__iexact=obj.class_name.strip(),
                date=obj.date,
                venue__iexact=obj.venue.strip(),
            )

            if not class_qs.exists():
                raise ValidationError(
                    f"No class found for {obj.class_name} on {obj.date} at {obj.venue}"
                )

            if class_qs.count() > 1:
                raise ValidationError(
                    "Multiple matching classes found. Please refine start/end time."
                )

            obj.class_obj = class_qs.first()

        if change:
            old = Attendance.objects.get(pk=obj.pk)

            if old.attended != obj.attended:
                if obj.attended:
                    obj.student.attendance += 1
                else:
                    obj.student.attendance -= 1
                
                if obj.student.attendance < 0:
                    obj.student.attendance = 0

                obj.student.save()
        else:
            if obj.attended:
                obj.student.attendance += 1
                obj.student.save()
                
        super().save_model(request, obj, form, change)


