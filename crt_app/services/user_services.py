from crt_app.models.user import Users
from crt_app.models.academic import *
from django.contrib.auth.hashers import make_password
from crt_app.utils.logger import log_info, log_error

class UserService:

    @staticmethod
    def create_instructor(name, email):
        try:
            log_info(f"Attempting to create instructor {email}")
            user = Users.objects.create(
                username = name,
                email = email,
                role = 'INSTRUCTOR',
                password = make_password("sober")
            )

            instructor = InstructorProfile.objects.create(
                user = user,
                full_name= name
            )

            log_info(f"Instructor created -> {email}")
            return instructor
    
        except Exception as e:
            log_error(f"Instructor creation failed -> {str(e)}")
            raise

    def create_student(data):
        try:
            log_info(f"Attempting to create student -> {data['stu_email']}")
            user = Users.objects.create(
                username = data["name"],
                email = data["email"],
                role = 'STUDENT',
                password = make_password(data["rtu_roll_no"])
            )
            tpo_ = TPOProfile.objects.get(
                tpo_email = data['tpo_email']
            )
            student = StudentProfile.objects.create(
                student = user,
                tpo = tpo_,
                stu_name = data['stu_name'],
                stu_email = data['stu_email'],
                rtu_roll_no = data['rtu_roll_no'],
                branch = data['branch'],
                attendance = data['attendance'],
                tpo_email = data["tpo_email"]
            )

            log_info(f"Successfully created student {data['stu_email']}")
            return student
        
        except Exception as e:
            log_error(f"Student Creation failed -> {str(e)}")

