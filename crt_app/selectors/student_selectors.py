from crt_app.models.academic import StudentProfile

class StudentSelector:

    @staticmethod
    def get_students_for_user(user):
        if user.role == "STUDENT":
            return StudentProfile.objects.filter(user=user)
        
        if user.role == "TPO":
            return StudentProfile.objects.filter(tpo = user.tpo_profile).select_related('user')
        
        if user.role == "INSTRUCTOR":
            return StudentProfile.objects.filter(
                attendance__class_obj__instructor = user.instructor_profile).distinct()
        
        if user.role == "INTERVIEWER":
            return StudentProfile.objects.filter(
                performance__interviewer = user.interviewer_profile).distinct()
        
        return StudentProfile.objects.none()
    

    @staticmethod
    def get_student_by_id(user, student_id):

        student = StudentProfile.objects.filter(id = student_id).first()

        from crt_app.permissions.access import Access_Control

        if not student or not Access_Control.can_access_student(user, student):
            return None
        
        return student