from crt_app.models.academic import Classes, InstructorProfile
from crt_app.utils.logger import log_info, log_error

class ClassServices:

    @staticmethod
    def create_class(data):
        try:
            log_info(f"Attempting to create class -> {data['class_name']}")
            instructor_ = InstructorProfile.objects.get(ins_email = data['ins_email'])

            created_class = Classes.objects.create(
                instructor = instructor_,
                date = data['date'],
                start_time = data['start_time'],
                end_time = data['end_time'],
                venue = data['venue']
            )

            log_info(f"Successfully created Class -> {data['classname']}")
            return created_class

        except Exception as e:
            log_error(f"Class creation failed -> {str(e)}")
            raise e