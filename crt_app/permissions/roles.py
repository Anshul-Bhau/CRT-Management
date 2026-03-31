class Role_Checker:
    @staticmethod
    def is_tpo(user):
        return user.role == 'TPO'
    
    @staticmethod
    def is_student(user):
        return user.role == 'STUDENT'
    
    @staticmethod
    def is_instructor(user):
        return user.role == 'INSTRUCTOR'
    
    @staticmethod
    def is_interviewer(user):
        return user.role == 'INTERVIEWER'