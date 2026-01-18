from crt_app.models.academic import StudentProfile, InterviewerProfile
from crt_app.models.performance import Performance
from crt_app.utils.logger import log_info, log_error

class PerformanceServices:

    @staticmethod
    def create_performance(data):
        try:
            log_info(f"Attempting to create performance for -> {data['stu_email']}")
            interviewer_ = InterviewerProfile.objects.get(user__email = data['int_email'])
            student_ = StudentProfile.objects.get(stu_email = data['stu_email'])
            performance= Performance.objects.create(
                interviewer = interviewer_,
                student = student_,
                stu_name = data['stu_name'],
                stu_email = data['stu_email'],
                int_email = data['int_email'],
                subject = data['subject'],
                date = data['date'],
                remark = data['remark'],
                score = data['score']
            )

            log_info(f"Successfully created performance for -> {data['stu_email']}")
            return performance

        except Exception as e:
            log_error(f"Class creation failed -> {str(e)}")
            raise e