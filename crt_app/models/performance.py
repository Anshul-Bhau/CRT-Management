from django.db import models
from crt_app.models.academic import StudentProfile, InterviewerProfile


class Performance(models.Model):

    SUB_CHOICES = [
        ('TECH', 'TECH'),
        ('HR', 'HR'),
        ('GD_EXTEMPORE', 'GD_EXTEMPORE')
    ]

    interviewer = models.OneToOneField(
        InterviewerProfile,
        on_delete=models.SET_NULL,
        related_name='interviewer_profile',
        null=True
    )

    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='student_performance'
    )
    
    stu_name = models.CharField(max_length=250, unique=False, blank=False)
    stu_email = models.EmailField(null=False)
    int_email = models.EmailField(null=False)
    subject = models.CharField(choices=SUB_CHOICES, max_length=70, null=False, blank=False)
    date = models.DateField(null=True)
    remark = models.TextField(null=True, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.subject} marks of {self.student.stu_name} at {self.date}"
    

