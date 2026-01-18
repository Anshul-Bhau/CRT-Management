from crt_app.models.user import Users
from crt_app.models.academic import *
from django.contrib.auth.hashers import make_password
from crt_app.utils.logger import log_info, log_error

class UserService:

    @staticmethod
    def create_instructor(data):
        try:
            log_info(f"Attempting to create instructor -> {data['email']}")
            user = Users.objects.create(
                username = data['name'],
                email = data['email'],
                role = 'INSTRUCTOR',
                password = make_password("sober")
            )

            instructor = InstructorProfile.objects.create(
                user = user,
                full_name= data['name']
            )

            log_info(f"Instructor created -> {data['email']}")
            return instructor
    
        except Exception as e:
            log_error(f"Instructor creation failed -> {str(e)}")
            raise e

    @staticmethod
    def create_student(data):
        try:
            log_info(f"Attempting to create student -> {data['stu_email']}")
            user_ = Users.objects.create(
                username = data["stu_name"],
                email = data["stu_email"],
                role = 'STUDENT',
                password = make_password(data["rtu_roll_no"])
            )
            tpo_ = TPOProfile.objects.get(
                tpo_email = data['tpo_email']
            )
            student = StudentProfile.objects.create(
                user = user_,
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
            raise e

    @staticmethod
    def create_tpo(data):
        try:
            log_info(f"Attempting to create tpo -> {data['tpo_email']}")
            user_ = Users.objects.create(
                username = data['tpo_name'],
                email  = data['tpo_email'],
                role = 'TPO',
                password = make_password('sober')
            )

            tpo = TPOProfile.objects.create(
                user = user_,
                tpo_name = data['tpo_name'],
                tpo_email = data['tpo_email'],
                # branch = data['branch'],
                # batch = data['batch']
            )
            log_info(f"Successfully created tpo {data['tpo_email']}")
            return tpo
        
        except Exception as e:
            log_error(f"Tpo creation failed -> {str(e)}")
            raise e

    @staticmethod
    def create_interviewer(data):
        try:
            log_info(f"Attempting to create interviewer -> {data['inter_email']}")
            user_ = Users.objects.create(
                    username = data['inter_name'],
                    email  = data['inter_email'],
                    role = 'INTERVIEWER',
                    password = make_password('sober')
                )
            interviewer = InterviewerProfile(
                user = user_,
                sub = data['sub']
            )
            log_info(f"Successfully created interviewer {data['inter_email']}")
            return interviewer
        
        except Exception as e:
            log_error(f"Interviewer creation failed -> {str(e)}")
            raise e
    
