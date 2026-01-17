from django.contrib import admin
from .models.academic import *
from .models.attendance import Attendance
from crt_app.utils.logger import log_info, log_error


@admin.register(Users)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'email')

    def save_model(self, request, obj, form, change):
        log_info(f"User modified: {obj.username}")
        super().save_model(request, obj, form, change)


admin.site.register(StudentProfile)
admin.site.register(InstructorProfile)
admin.site.register(TPOProfile)
admin.site.register(Attendance)
