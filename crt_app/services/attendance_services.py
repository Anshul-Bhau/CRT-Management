from crt_app.models.academic import Classes, StudentProfile
from crt_app.utils.logger import log_info, log_error

class AttendanceServices:

    @staticmethod
    def create_attendance(data):
        try:
            log_info(f"Attempting to create attendance -> {data['stu_name']}")
            student_ = StudentProfile.objects.get(stu_email = data['stu_email'])
            class_ = Classes.objects.get(class_name = data['class_name'], 
                                        date = data['date'], 
                                        start_time = data['start_time'], 
                                        end_time = data['end_time'], 
                                        venue = data['venue'])
            created_class = Classes.objects.create(
                student = student_,
                class_obj = class_,
                class_name = data['class_name'],
                stu_name = data['stu_name'],
                stu_email = data['stu_email'],
                start_time = data['start_time'],
                end_time = data['end_time'],
                venue = data['venue'],
                date = data['date'],
                attended = data['attended']
            )

            log_info(f"Successfully created Class -> {data['classname']}")
            return created_class

        except Exception as e:
            log_error(f"Class creation failed -> {str(e)}")
            raise e