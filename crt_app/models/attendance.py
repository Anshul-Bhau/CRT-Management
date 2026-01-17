from django.db import models
from crt_app.models.academic import StudentProfile, Classes

class Attendance(models.Model):
    
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    class_name = models.OneToOneField(
        Classes,
        on_delete=models.SET_NULL,
        related_name="class_object",
        null=True
    )

    date  = models.DateField(null=False, blank=False)
    attended = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        if self.attended == True:
            return f"{self.student.stu_email} was Present for {self.class_name.class_name} on {self.date}"
        else:
            return f"{self.student.stu_email} was Present for {self.class_name.class_name} on {self.date}"