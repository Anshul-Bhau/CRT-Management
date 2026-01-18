from django.db import models
from .user import Users
from django.core.exceptions import ValidationError

class InstructorProfile(models.Model):

    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        related_name='instructor_profile'
    )
    ins_email = models.EmailField(null=False)
    ins_name = models.CharField(max_length=250, unique=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ins_email

class TPOProfile(models.Model):
    user = models.OneToOneField(
        Users, 
        on_delete=models.CASCADE,
        related_name='tpo_profile'
    )
    tpo_name = models.CharField(max_length=250, unique=False, null=False)
    tpo_email = models.EmailField(max_length=250, unique=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tpo_email

class StudentProfile(models.Model):

    user = models.OneToOneField(
        Users, 
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    tpo = models.OneToOneField(
        TPOProfile,
        on_delete=models.SET_NULL,
        related_name='tpo_profile',
        null=True
    )
    
    BRANCH_CHOICES= [('CSE', 'CSE'),
                        ('AIDS', 'AIDS'),
                        ('MECH', 'MECH'),
                        ('ELEC', 'ELEC'),
                        ('CIVIL', 'CIVIL'),
                        ('ECE', 'ECE'),
                        ('IT', 'IT'),
                        ('CSAI', 'CSAI')]
    
    stu_name = models.CharField(max_length=250, unique=False, blank=False, null=False)
    stu_email = models.EmailField(max_length=200, null=False, blank=False)
    rtu_roll_no = models.CharField(max_length=30, unique=True, null = False, blank= False)
    branch = models.CharField(max_length= 25, null=False, choices=BRANCH_CHOICES)
    attendance = models.IntegerField(default=0)
    tpo_email = models.EmailField(max_length=250, unique=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # batch_id = models.CharField(max_length=120, null=False, blank=False)
    # batch_name = models.CharField(max_length=10, null=False)
    # score = models.IntegerField(default=0)
    
    def __str__(self):
        return self.stu_email
    
class InterviewerProfile(models.Model):
    SUBJECT_CHOICES = [ ('TECH', 'TECH'),
                        ('HR', 'HR'),
                        ('GD_EXTEMPORE', 'GD_EXTEMPORE')]
    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        related_name='interviewer_profile'
    )
    int_name = models.CharField(max_length=250, unique=False, blank=False, null=False)
    int_email = models.EmailField(max_length=200, null=False, blank=False)
    sub = models.CharField(max_length=50, null=False, choices=SUBJECT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}"

    
class Classes(models.Model):

    instructor = models.OneToOneField(
        InstructorProfile,
        on_delete=models.SET_NULL,
        related_name='instructor_profile',
        null=True
    )

    class_name = models.CharField(max_length=250 ,null=False, unique=False)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=250)

    # batch_name = models.CharField(max_length=50, null=False)
    # batch_id = models.IntegerField(null=False)

    def check_date(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date must be after start date")

    def __str__(self):
        return f"{self.class_name} at {self.date}"
    