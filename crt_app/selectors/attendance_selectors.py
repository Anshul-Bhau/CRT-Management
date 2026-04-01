from crt_app.models import Attendance

class AttendanceSelectors:
    @staticmethod
    def get_attendance_for_user(user):
        
        if user.role == "STUDENT":
            return Attendance.objects.filter(
                student__user = user
            ).select_related('class_obj')
        
        if user.role == "TPO":
            return Attendance.objects.filter(
                student__tpo = user.tpo_profile
            ).select_related('student', 'class_obj')
        
        if user.role == "INSTRUCTOR":
            return Attendance.objects.filter(
                class_obj__instructor = user.instructor_profile
            ).select_related('student', 'class_obj')
        
        return Attendance.objects.none()
    
    @staticmethod
    def get_attendance_by_student(user, student):
        from crt_app.permissions.access import Access_Control

        if not Access_Control.can_access_student(user, student):
            return Attendance.objects.none()
        
        return Attendance.objects.filter(
            student=student
        ).select_related('class_obj', 'student', 'class_obj__instructor')