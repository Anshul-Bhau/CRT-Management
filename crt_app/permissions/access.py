from crt_app.permissions.roles import Role_Checker

class Access_Control:
    @staticmethod
    def can_access_student(user, student):
        if Role_Checker.is_student(user):
            return student.user_id == user.id
        
        if Role_Checker.is_tpo(user):
            return student.tpo_id == user.tpo_profile.id
        
        if Role_Checker.is_instructor(user):
            return student.attendance_set.filter(
                class_obj__instructor= user.instructor_profile
            ).exists()
        
        if Role_Checker.is_interviewer(user):
            return student.performance_set.filter(
                interviewer = user.interviewer_profile
            ).exists()
        
        return False
    
    @staticmethod
    def can_access_attendance(user, attendance):
        if Role_Checker.is_student(user):
            return attendance.student.user_id == user.id
        
        if Role_Checker.is_tpo(user):
            return attendance.strudent.tpo_id == user.tpo_profile.id
        
        if Role_Checker.is_instructor(user):
            return attendance.class_obj.instructor_id == user.instructor_profile.id
        
        return False
    
    @staticmethod
    def can_access_performance(user, performance):
        if Role_Checker.is_student(user):
            return performance.student.user_id == user.id
        
        if Role_Checker.is_tpo(user):
            return performance.student.tpo_id == user.tpo_profile.id
        
        if Role_Checker.is_interviewer(user):
            return performance.interviewer_id == user.interviewer_profile.id
        
        return False
    