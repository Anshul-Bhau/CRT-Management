from django.db import models
from crt_app.models.academic import StudentProfile, Classes

class Attendance(models.Model):
    
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    class_obj = models.OneToOneField(
        Classes,
        on_delete=models.SET_NULL,
        related_name="class_object",
        null=True
    )

    class_name = models.CharField(max_length=250 ,null=False, unique=False)
    stu_name = models.CharField(max_length=250, unique=False, blank=False)
    stu_email = models.EmailField(null=False)
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=250)
    date  = models.DateField(null=False, blank=False)
    attended = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        if self.attended == True:
            return f"{self.student.stu_email} was Present for {self.class_name.class_name} on {self.date}"
        else:
            return f"{self.student.stu_email} was Present for {self.class_name.class_name} on {self.date}"