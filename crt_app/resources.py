from django.forms import ValidationError
from django.contrib.auth.hashers import make_password
from import_export import resources, fields
from django.db import transaction
from .models import *
from import_export.widgets import ForeignKeyWidget

class UserResource(resources.ModelResource):
    class Meta:
        model = Users
        fields = ('last_login', 'is_superuser', 'groups', 'user_permissions', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'id', 'username', 'email', 'password', 'role', 'phone_no', 'user_created_at')
        export_order = ('last_login', 'is_superuser', 'groups', 'user_permissions', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'id', 'username', 'email', 'password', 'role', 'phone_no', 'user_created_at')

class StudentResource(resources.ModelResource):
    user = fields.Field(column_name='stu_email', attribute='user', widget=ForeignKeyWidget(Users, 'email'))
    tpo = fields.Field(column_name='tpo_email', attribute='tpo', widget=ForeignKeyWidget(TPOProfile, 'tpo_email'))

    class Meta:
        model = StudentProfile
        exclude = ('student_created_at',)
        fields = ('stu_name', 'stu_email', 'rtu_roll_no', 'branch','attendance', 'score', 'tpo_email')
        export_order = ('stu_name', 'stu_email', 'rtu_roll_no', 'branch', 'attendance', 'score', 'tpo_email')
        import_id_fields = ('rtu_roll_no',)

    def before_import_row(self, row, **kwargs):
        user, created = Users.objects.get_or_create(
            email = row['stu_email'],
            defaults={
                'username' : row['stu_name'],
                'role' : 'STUDENT',
                'password': make_password(row['rtu_roll_no'])
            }
        )

        if not TPOProfile.objects.filter(tpo_email = row['tpo_email']).exists():
            raise ValidationError(
                f"TPO not found -> {row['tpo_email']}"
            )

class AttendanceResource(resources.ModelResource):

    student = fields.Field(
        column_name='stu_email',
        attribute='student',
        widget=ForeignKeyWidget(StudentProfile, 'stu_email')
    )

    class_obj = fields.Field(
        column_name='class_name',
        attribute='class_obj',
        widget=ForeignKeyWidget(Classes, 'class_name')
    )

    class Meta:
        model = Attendance

        fields = (
            'stu_email', 'class_name', 'date', 'start_time', 'end_time', 'venue', 'attended',
        )

        import_id_fields = (
            'stu_email',
            'class_name',
            'date',
        )

        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        row["attended"] = str(row.get("attended")).strip().lower() in [
            "1", "true", "yes", "present"
        ]

        
        if not StudentProfile.objects.filter(stu_email=row["stu_email"]).exists():
            raise ValueError(f"Student not found → {row['stu_email']}")

        
        if not Classes.objects.filter(
            class_name=row["class_name"],
            date=row["date"]
        ).exists():
            raise ValueError(f"Class not found → {row['class_name']} on {row['date']}")
    
    @transaction.atomic
    def after_save_instance(self, instance, row, **kwargs):
        if instance.attended:
            student = instance.student
            student.attendance += 1
            student.save()


class InstructorResource(resources.ModelResource):
    
    class Meta:
        model = InstructorProfile
        exclude = ('id', 'created_at')
        import_id_fields = ['ins_email']
        fields = ('ins_name', 'ins_email')
        export_order = ('ins_name', 'ins_email')
    
    def before_import_row(self, row, **kwargs):

        user, created = Users.objects.get_or_create(
            email=row['ins_email'],
            defaults={
                'username': row['ins_name'],
                'role': 'INSTRUCTOR',
                'password': make_password("sober")
            }
        )

        InstructorProfile.objects.get_or_create(
            ins_email=row['ins_email'],
            defaults={
                'ins_name': row['ins_name'],
                'user': user
            }
        )
    
class ClassesResource(resources.ModelResource):
    instructor = fields.Field(column_name='ins_email', attribute='instructor', widget=ForeignKeyWidget(InstructorProfile, 'ins_email'))

    class Meta:
        model = Classes
        exclude = ('id',)
        import_id_fields = ["ins_email", "class_name", 'date', 'start_time', 'end_time','venue']
        fields = ("ins_email", "class_name", 'date', 'start_time', 'end_time','venue')
        export_order = fields
    
    def before_import_row(self, row, **kwargs):
        if not InstructorProfile.objects.filter(
            ins_email=row['ins_email']
        ).exists():
            raise ValidationError(
                f"Instructor not found -> {row['ins_email']}"
            )
    

class TPOResource(resources.ModelResource):
    class Meta:
        model = TPOProfile
        exclude = ('id', 'created_at')
        import_id_fields = ['tpo_email']
        fields = ('tpo_name', 'tpo_email')
        export_order = ('tpo_name', 'tpo_email')
    
    def before_import_row(self, row, **kwargs):
            user, _ = Users.objects.get_or_create(
                email=row['tpo_email'],
                defaults= {
                    'username': row['tpo_name'],
                    'role' : 'TPO',
                    'password' : make_password("sober")
                }
            )
            
            TPOProfile.objects.get_or_create(
                tpo_email = row['tpo_email'],
                defaults={
                    'tpo_name' : row['tpo_name'],
                    'user' : user
                }
            )

    


class InterviewerResource(resources.ModelResource):
    user = fields.Field(column_name='int_email', attribute='user', widget=ForeignKeyWidget(Users, 'email'))

    class Meta:
        model = InterviewerProfile
        
        fields = ('int_name', 'int_email', 'sub')
        export_order = fields
        import_id_fields = ('int_emails',)

        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        user, _ = Users.objects.get_or_create(
            email=row['int_email'],
            defaults={
                'username': row['int_name'],
                'role': 'INTERVIEWER',
                'password' : make_password("sober")
            }
        )

        InterviewerProfile.objects.get_or_create(
            int_email = row['int_email'],
            defaults={
                'int_name' : row['int_name'],
                'sub' : row['sub'],
                'user' : user
            }
        )



