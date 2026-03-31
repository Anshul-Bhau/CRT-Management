from crt_app.models import Performance

class PerformanceSelector:
    @staticmethod
    def get_performance_for_user(user):
        if user.role == "STUDENT":
            return Performance.objects.filter(
                student__user = user
            )
        
        if user.role == "TPO":
            return Performance.objects.filter(
                student__tpo = user.tpo_profile
            ).select_related('student')
        
        if user.role == "INTERVIEWER":
            return Performance.objects.filter(
                interviewer = user.interviewer_profile
            ).select_related('student')
        
        return Performance.objects.none()

    @staticmethod
    def get_performance_by_student(user, student):
        from crt_app.permissions.access import Access_Control

        if not student or Access_Control.can_access_performance(user, student):
            return Performance.objects.none()
        
        return Performance.objects.filter(student=student)