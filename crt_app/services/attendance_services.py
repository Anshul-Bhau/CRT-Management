from django.db import transaction
from crt_app.models.academic import Classes, StudentProfile
from crt_app.models.attendance import Attendance
from crt_app.utils.logger import log_info, log_error

class AttendanceServices:

    @staticmethod
    @transaction.atomic
    def mark_attendance(data):
        try:
            log_info(f"Attempting to create attendance -> {data['stu_name']}")
            student_ = StudentProfile.objects.get(stu_email = data['stu_email'])
            class_ = Classes.objects.get(class_name = data['class_name'], 
                                        date = data['date'], 
                                        start_time = data['start_time'], 
                                        end_time = data['end_time'], 
                                        venue = data['venue'])

            exists = Attendance.objects.filter(
                student=student_,
                class_obj=class_,
                date=data['date']
            ).exists()

            if exists:
                raise ValueError("Attendance already marked")
            
            attendance = Attendance.objects.create(
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
            if data['attended']:
                student_.attendance += 1
                student_.save()

            log_info(f"Successfully created Class -> {data['classname']}")
            return attendance

        except Exception as e:
            log_error(f"Class creation failed -> {str(e)}")
            raise e
    
    @staticmethod
    @transaction.atomic
    def update_attendance(attendance_id, attended_status):

        try:
            record = Attendance.objects.get(id=attendance_id)
            student = record.student

            if record.attended != attended_status:
                if attended_status:
                    student.attendance += 1
                else:
                    student.attendance -= 1

                student.save()

            record.attended = attended_status
            record.save()

            return record

        except Attendance.DoesNotExist:
            raise ValueError("Attendance record not found")
