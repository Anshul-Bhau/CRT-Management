from django.db import models

# Create your models here.
from django.db import models
from django.db import transaction
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import uuid


class Users(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    Role_Choices = [('student', 'Student'),
                    ('instructor', 'Instructor'),
                    ('hod', 'HOD'),
                    ('tpo', 'TPO'),
                    ('interviewer', 'Interviewer'),
                    ('admin', 'Admin')]
    username = models.CharField(max_length=150, unique=False, null=False, blank=False)
    email = models.EmailField(max_length=150, unique=True,blank=False)
    password = models.CharField(max_length=150, blank=False, null=False)
    role  = models.CharField(max_length=25,null=False, blank=False, choices=Role_Choices)
    phone_no = models.PositiveBigIntegerField(null=True, blank= True)
    user_created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role', 'username', 'password']
    
    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_'):  # Avoids re-hashing of the password 
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

        self.create_passw_instance()
    
    def create_passw_instance(self):
        try:
            Passwords.objects.get_or_create(
                user=self,
                defaults={
                    'username': self.username,
                    'user_email' : self.email,
                    'password': self.password
                    })
        except Exception as e:
            print(f"Error creating Passwords record: {e}")

    def __str__(self):
        return f"{self.username} is {self.role}"

class Instructor(models.Model):
    instructor = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='instructor_profile')
    ins_name = models.CharField(max_length=250, unique=False, blank=False, null=False)
    ins_email = models.EmailField(max_length=200, null=False, blank=False)
    ins_created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.instructor_id:  
                user = Users(
                    username=self.ins_name,
                    email=self.ins_email,
                    role='instructor',
                    password= make_password("sober"))
                user.save()
                self.instructor = user
        
            super().save(*args, **kwargs)

            # Assign staff status and permissions
            self.assign_perms_ins()

    def assign_perms_ins(self):
        try:
            Users.objects.filter(pk=self.instructor.pk).update(is_staff=True)
        except Exception as e:
            print(f"Error setting is_staff for instructor : {e}")

    def __str__(self):
        return f"{self.instructor.username}"


class Classes(models.Model):
    phase_choices = [('1', 'one'),
                        ('2', 'two'),
                        ('3', 'three')]
    class_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    phase = models.CharField(max_length= 50, null=False, blank=False, choices=phase_choices) #add choice ---> Done
    class_name = models.CharField(max_length=100)
    date = models.DateField(null=True)
    start_time = models.TimeField()
    end_time = models.TimeField(null = True)
    venue = models.CharField(max_length=150)
    total_students = models.IntegerField()
    ins_email = models.EmailField(max_length=250, null= False, blank=False)
    ins_name = models.CharField(max_length=250, null= False, blank=False)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, null=False, related_name='classes')
    batch_id = models.IntegerField(null = False)
    batch_name = models.CharField(max_length= 10, null=False)
    class_created_at = models.DateTimeField(auto_now_add=True)

    def check_time(self):
        if self.end_time < self.start_time:
            raise ValidationError("End time must be after start time")

    def save(self, *args, **kwargs):
            self.check_time()
            self.instructor = Instructor.objects.get(ins_email = self.ins_email)
            super().save(*args, **kwargs)


# -- Tell the overall roadmap of CRT,
#       DAT-1, orientation, phase1, Dat-2, etc.
# add class id
# boolean for all or particular
class Schedule(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100, null=False)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null = True)
    description = models.TextField(null = True, blank= True)

    def check_date(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date must be after start date")

class TPO(models.Model):
    tpo = models.OneToOneField(Users, on_delete=models.CASCADE)
    tpo_name = models.CharField(max_length=250, unique=False, blank=False, null=False)
    tpo_email = models.EmailField(max_length=200, null=False, blank=False)
    branch_choices = [('CSE', 'CSE'),           
                        ('AIDS', 'AIDS'),       
                        ('MECH', 'MECH'),       
                        ('ELEC', 'ELEC'),       
                        ('CIVIL', 'CIVIL'),     
                        ('ECE', 'ECE'),         
                        ('IT', 'IT'),
                        ('CSAI', 'CSAI')]
    branch = models.CharField(max_length= 25, null=False, choices=branch_choices)
    batch = models.CharField(max_length=25, null =False, blank=False)
    tpo_created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        with transaction.atomic():
            try:
                user = Users.objects.get(email=self.tpo_email)
            except Users.DoesNotExist:
                user = Users(
                    email=self.tpo_email,
                    username=self.tpo_name,
                    role='tpo',
                    password=make_password('sober')
                )
                user.save()
            self.tpo = user
            super().save(*args, **kwargs)

            # Assign staff status and permissions
            self.tpo_perms_and_is_staff()

    def tpo_perms_and_is_staff(self):
        permissions = ['view_student', 'view_gd_extemporeperformance', 'view_hrperformance', 'view_techperformance']
        for perm_codename in permissions:
            try:
                perm = Permission.objects.get(codename=perm_codename)
                self.tpo.user_permissions.add(perm)
            except Permission.DoesNotExist:
                print(f"Permission {perm_codename} not found.")
        self.tpo.is_staff = True
        self.tpo.save()

    def __str__(self):
        return f"{self.tpo.username} of {self.branch}"

class Interviewer(models.Model):
    sub_choices = [('Tech', 'Tech'),
                    ('Hr', 'Hr'),
                    ('Gd_extempore', 'Gd_extempore'),]
    interviewer = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='interviewer_profile', null=True, blank=True) # dynammically set
    inter_name = models.CharField(max_length=250, unique=True, blank=False, null=False)
    inter_email = models.EmailField(max_length=225, unique=True, blank=False, null =False)
    sub = models.CharField(max_length=50, null=False, choices=sub_choices)

    def __str__(self):
        return f"{self.interviewer.username}"


class Student(models.Model):
    branch_choices = [('CSE', 'CSE'),
                        ('AIDS', 'AIDS'),
                        ('MECH', 'MECH'),
                        ('ELEC', 'ELEC'),
                        ('CIVIL', 'CIVIL'),
                        ('ECE', 'ECE'),
                        ('IT', 'IT'),
                        ('CSAI', 'CSAI')]

    phase_choices = [(1, 'one'),
                        (2, 'two'),
                        (3, 'three')]

    student = models.OneToOneField(Users, on_delete=models.CASCADE, related_name= 'Student_profile', null=True) # dynammically set so made null as true
    stu_name = models.CharField(max_length=250, unique=False, blank=False, null=False)
    stu_email = models.EmailField(max_length=200, null=False, blank=False)
    rtu_roll_no = models.CharField(max_length=30, unique=True, null = False, blank= False)
    branch = models.CharField(max_length= 25, null=False, choices=branch_choices)
    # password = models.CharField(max_length=20, null= False, blank=False, default="sober") #Temporary default
    batch_id = models.CharField(max_length=120, null=False, blank=False)
    batch_name = models.CharField(max_length=10, null=False)
    attendance = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    tpo_name = models.CharField(max_length=250, unique=False, null=False)
    tpo = models.ForeignKey(TPO, on_delete=models.DO_NOTHING, related_name="student_tpo")
    phase = models.IntegerField(null=False, choices=phase_choices)
    stu_created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} having roll number {self.rtu_roll_no}"
    
    
    def create_batch_editors(self):
        batch_name = self.batch_name
        print(batch_name)
        roles = ["techperformance", "hrperformance", "gd_extemporeperformance"]
        interviewers = {}

        for role in roles:
            group_name = f"{batch_name}_{role}_interviewer"
            group, group_created = Group.objects.get_or_create(name=group_name)
            if group_created:
                print(f"new grp {group}")
                try:
                    permissions = Permission.objects.filter(codename__in=[f"view_{role}", f"add_{role}"])
                    if not permissions.exists():
                        print(f"Permissions not found for role: {role}")
                        continue
                    group.permissions.add(*permissions)
                except Exception as e:
                    print(f"Error adding permissions: {e}")
                    continue

            role_type = role.replace("performance", "").capitalize()
            email = f"{batch_name}_{role_type}_interviewer7@gmail.com"
            username = f"{batch_name}_{role_type}_interviewer"
            password = "sober"

            user, created = Users.objects.get_or_create(
                email=email,
                username= username,
                role= "interviewer",
                is_staff= True)
            user.password = make_password(password)
            print(user, user.username, user.email)

            if created:
                print(f"User created - {user}")
                user.groups.add(group)
                user.save()
            else:
                print(f"User already exists - {user}")

            interviewer, int_created = Interviewer.objects.get_or_create(
                interviewer=user,
                inter_name = username,
                inter_email = email,
                sub = role_type)

            if int_created:
                print(f"Interviewer created - {interviewer}")

            interviewers[role] = interviewer  # Store interviewer for each role

        return interviewers

    def create_performance_instances(self, interviewers):
        print(self, interviewers)

        if not TechPerformance.objects.filter(student=self).exists():
            TechPerformance.objects.create(student=self, stu_email=self.stu_email,interviewer=interviewers["techperformance"], interviewer_email=interviewers["techperformance"].inter_email)

        if not GD_ExtemporePerformance.objects.filter(student=self).exists():
            GD_ExtemporePerformance.objects.create(student=self, stu_email=self.stu_email, interviewer=interviewers["gd_extemporeperformance"], interviewer_email=interviewers["gd_extemporeperformance"].inter_email)

        if not HRPerformance.objects.filter(student=self).exists():
            HRPerformance.objects.create(student=self, stu_email=self.stu_email, interviewer=interviewers["hrperformance"], interviewer_email=interviewers["hrperformance"].inter_email)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.student_id:
                user = Users(
                    username=self.stu_name,
                    email=self.stu_email,
                    role='student',
                    password=make_password(self.rtu_roll_no)
                )
                user.save()
                self.student = user

            self.tpo = TPO.objects.get(tpo_name=self.tpo_name)
            super().save(*args, **kwargs)

            # Create interviewers and performance instances only once
            interviewers = self.create_batch_editors()
            self.create_performance_instances(interviewers)

class Passwords(models.Model):
    user = models.ForeignKey(Users, on_delete=models.DO_NOTHING)
    user_email = models.EmailField(max_length=250, null=False, blank=False)
    username = models.CharField(max_length=200, null=False, blank=False)
    password = models.CharField(max_length=150, null=False, blank=False)

class Attendance(models.Model):
    branch_choices = [('CSE', 'CSE'),
                        ('AIDS', 'AIDS'),
                        ('MECH', 'MECH'),
                        ('ELEC', 'ELEC'),
                        ('CIVIL', 'CIVIL'),
                        ('ECE', 'ECE'),
                        ('IT', 'IT'),
                        ('CSAI', 'CSAI')]

    phase_choices = [(1, 'one'),
                        (2, 'two'),
                        (3, 'three')]
    
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, related_name= 'student_attendance', null=True) # dynammically set so made null as true
    stu_name = models.CharField(max_length=250, unique=False, blank=False, null=False)
    date_time = models.DateTimeField(null=False, blank=False)
    stu_email = models.EmailField(max_length=200, null=False, blank=False)
    rtu_roll_no = models.CharField(max_length=30, unique=False, null = False, blank= False)
    branch = models.CharField(max_length= 25, null=False, choices=branch_choices)
    phase = models.IntegerField(null=False, choices=phase_choices)
    attended = models.BooleanField(null=False, blank=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            try:
                self.student = Student.objects.get(stu_email=self.stu_email)
            except Student.DoesNotExist:
                raise ValueError(f"No student found with email {self.stu_email}")
            
            is_new = not self.pk  # Checks if instance is new
            if not is_new:
                original = Attendance.objects.get(pk=self.pk)
                # proxy lag jayegi
                if original.attended != self.attended:
                    self.update_student_attendance(original.attended)
            else:
                # attendnace of new instances
                if self.attended:
                    self.student.attendance += 1
                    self.student.save()

            super().save(*args, **kwargs)

    def update_student_attendance(self, original_status):
        if original_status and not self.attended:
            self.student.attendance -= 1  
        elif not original_status and self.attended:
            self.student.attendance += 1 
        self.student.student.save()

class Announcements(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_announcements')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Batch_announcements(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="sent_batch_announcements")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add= True)
    batch = models.CharField(max_length=25, null=False, blank=False)

class TechPerformance(models.Model):
    round_choices = [('R1', 'round1' ), ('R2', 'round2'), ('R3', 'round3'), ('R4', 'round4')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="tech_performance")
    stu_email = models.EmailField(max_length=250, null=True, unique=True, blank=True)
    interviewer = models.ForeignKey(Interviewer, on_delete=models.CASCADE, related_name="tech_interviewer", null=True, blank=True) # to_fileds removed
    interviewer_email = models.EmailField(max_length=250, null=True, unique=False, blank=True)
    interviewer_name = models.CharField(max_length=250, null=True, unique=False, blank=False)
    date = models.DateField(null = True)
    round = models.CharField(choices=round_choices, max_length=40, null=True, blank=True)
    remark = models.TextField(null = True, blank = True)
    score = models.PositiveIntegerField(null = True, blank=True)


class GD_ExtemporePerformance(models.Model):
    round_choices = [('R1', 'round1' ), ('R2', 'round2'), ('R3', 'round3'), ('R4', 'round4')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="gd_extempore_performance")
    stu_email = models.EmailField(max_length=250, null=True, unique=True, blank=True)
    interviewer = models.ForeignKey(Interviewer, on_delete=models.CASCADE, related_name="gd_extempore_interviewer", null = True, blank=True)
    interviewer_email = models.EmailField(max_length=250, null=True, unique=False, blank=True)
    interviewer_name = models.CharField(max_length=250, null=True, unique=False, blank=False)
    date = models.DateField(null = True)
    round = models.CharField(choices=round_choices, max_length=40, null=True, blank=True)
    remark = models.TextField(null = True, blank = True)
    score = models.PositiveIntegerField(null = True, blank=True)

class HRPerformance(models.Model):
    round_choices = [('R1', 'round1' ), ('R2', 'round2'), ('R3', 'round3'), ('R4', 'round4')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="hr_performance")
    stu_email = models.EmailField(max_length=250, null=True, unique=True, blank=True)
    interviewer = models.ForeignKey(Interviewer, on_delete=models.CASCADE, related_name="hr_interviewer", null=True, blank=True)
    interviewer_email = models.EmailField(max_length=250, null=True, unique=False, blank=True)
    interviewer_name = models.CharField(max_length=250, null=True, unique=False, blank=False)
    date = models.DateField(null = True)
    round = models.CharField(choices=round_choices, max_length=40, null=True, blank=True)
    remark = models.TextField(null = True, blank = True)
    score = models.PositiveIntegerField(null = True, blank=True)
        


