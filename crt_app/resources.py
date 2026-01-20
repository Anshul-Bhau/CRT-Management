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

        skip_unchanged = True
        report_skipped = True

    def before_import(self, dataset, **kwargs):
        size = len(dataset.dict)

        # ─── SMALL FILE MODE ───
        if size <= 200:
            self.use_bulk = False
            self.batch_size = 50

        # ─── LARGE FILE MODE ───
        else:
            self.use_bulk = True
            self.batch_size = 1000

        emails = [r['stu_email'] for r in dataset.dict]
        tpo_emails = [r['tpo_email'] for r in dataset.dict]

        existing_users = set(
            Users.objects.filter(email__in=emails)
            .values_list('email', flat=True)
        )

        valid_tpos = set(
            TPOProfile.objects.filter(tpo_email__in=tpo_emails)
            .values_list('tpo_email', flat=True)
        )

        users_to_create = []

        for row in dataset.dict:

            if row['tpo_email'] not in valid_tpos:
                raise ValueError(
                    f"TPO not found → {row['tpo_email']}"
                )

            if row['stu_email'] not in existing_users:

                u = Users(
                    username=row['stu_name'],
                    email=row['stu_email'],
                    role='STUDENT'
                )

                u.set_password(row['rtu_roll_no'])
                users_to_create.append(u)

        if users_to_create:
            Users.objects.bulk_create(
                users_to_create,
                batch_size=self.batch_size
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
            'start_time',
            'venue'
        )

        skip_unchanged = True
        report_skipped = True

    def before_import(self, dataset, **kwargs):
        
        size = len(dataset.dict)

        # ─── SMALL FILE MODE ───
        if size <= 200:
            self.use_bulk = False
            self.batch_size = 50

        # ─── LARGE FILE MODE ───
        else:
            self.use_bulk = True
            self.batch_size = 1000
            
        self.student_cache = {
            s.stu_email : s for s in StudentProfile.objects.all()
        }

        self.class_cache = {}

        for c in Classes.objects.all():
            key = (
                c.class_name.strip().lower(),
                str(c.date),
                str(c.start_time),
                str(c.venue).strip().lower(),
            )
            self.class_cache[key] = c
    
    def before_import_row(self, row, **kwargs):
        row['attended'] = str(row.get("attended")).strip().lower() in ["1", "true", "yes", "present"]

        if row["stu_email"] not in self.student_cache:
            raise ValueError(f"Student not found -> {row['stu_email']}")
        
        key = (
            row["class_name"].strip().lower(),
            str(row["date"]),
            str(row["start_time"]),
            str(row["venue"]).strip().lower()
        )

        if key not in self.class_cache:
            raise ValueError(f"Class not found → {row['class_name']} "
                f"on {row['date']} at {row['venue']}")

        row["student"] = self.student_cache[row["stu_email"]]
        row["class_obj"] = self.class_cache[key]
    
    def get_instance(self, instance_loader, row):

        return Attendance.objects.filter(
            stu_email=row["stu_email"],
            class_name=row["class_name"],
            date=row["date"],
            start_time=row["start_time"],
            venue=row["venue"]
        ).first()
    
    def after_save_instance(self, instance, using_transactions, dry_run):
        if dry_run:
            return

        student = instance.student

        total = Attendance.objects.filter(
            student=student,
            attended=True
        ).count()

        student.attendance = total
        student.save()
        


class InstructorResource(resources.ModelResource):
    
    class Meta:
        model = InstructorProfile
        exclude = ('id', 'created_at')
        import_id_fields = ['ins_email']
        fields = ('ins_name', 'ins_email')
        export_order = ('ins_name', 'ins_email')

        skip_unchanged = True
        report_skipped = True

    def before_import(self, dataset, **kwargs):
        
        size = len(dataset.dict)

        # ─── SMALL FILE MODE ───
        if size <= 200:
            self.use_bulk = False
            self.batch_size = 50

        # ─── LARGE FILE MODE ───
        else:
            self.use_bulk = True
            self.batch_size = 1000
        
        self.user_cache = {
            u.email : u for u in Users.objects.all()
        }
        self.instructor_cache = {
            i.ins_email : i for i in InstructorProfile.objects.all()
        }
    
    def before_import_row(self, row, **kwargs):
        
        email = str(row.get('ins_email', '')).strip().lower()
        name = str(row.get('ins_name', '')).strip()

        if not email:
            raise ValueError("Instructor email missing")
        if not name: 
            raise ValueError("Instructor name missing")
        
        user = self.user_cache.get(email)
        if not user;
            user = Users.objects.create(
                email = email,
                username = name,
                role = 'INSTRUCTOR',
                password = make_password("sober")
                )
            self.user_cache[email] = user

        instructor = self.instructor_cache.get(email)

        if not instructor:
            instructor = InstructorProfile.objects.create(
                ins_email=email,
                ins_name=name,
                user=user
            )
            self.instructor_cache[email] = instructor

        row['id'] = instructor.id

class ClassesResource(resources.ModelResource):
    instructor = fields.Field(column_name='ins_email', attribute='instructor', widget=ForeignKeyWidget(InstructorProfile, 'ins_email'))

    class Meta:
        model = Classes
        exclude = ('id',)
        import_id_fields = ["ins_email", "class_name", 'date', 'start_time', 'end_time','venue']
        fields = ("ins_email", "class_name", 'date', 'start_time', 'end_time','venue')
        export_order = fields
        skip_unchanged = True
        report_skipped = True

    def before_import(self, dataset, **kwargs):

        size = len(dataset.dict)

        if size <= 200:
            self.use_bulk = False
            self.batch_size = 50
        else:
            self.use_bulk = True
            self.batch_size = 1000

        # cache instructors 
        self.ins_cache = {
            i.ins_email.strip().lower(): i
            for i in InstructorProfile.objects.all()
        }

        # cache existing classes
        self.class_cache = {
            (
                c.instructor.ins_email.strip().lower(),
                c.class_name.strip().lower(),
                str(c.date),
                str(c.start_time),
                str(c.end_time),
                c.venue.strip().lower(),
            ): c
            for c in Classes.objects.select_related("instructor")
        }


    # ─── VALIDATE EACH ROW ───
    def before_import_row(self, row, **kwargs):

        email = row['ins_email'].strip().lower()

        if email not in self.ins_cache:
            raise ValueError(f"Instructor not found → {email}")

        key = (
            email,
            row['class_name'].strip().lower(),
            str(row['date']),
            str(row['start_time']),
            str(row['end_time']),
            row['venue'].strip().lower(),
        )

        # prevent silent duplicates
        if key in self.class_cache:
            raise ValueError(
                f"Duplicate class → {row['class_name']} on {row['date']}"
            )

        row['instructor'] = self.ins_cache[email]


    # ─── UPDATE INSTEAD OF RECREATE ───
    def get_instance(self, instance_loader, row):

        return Classes.objects.filter(
            instructor__ins_email=row["ins_email"],
            class_name=row["class_name"],
            date=row["date"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            venue=row["venue"],
        ).first()
    
    

class TPOResource(resources.ModelResource):
    class Meta:
        model = TPOProfile
        exclude = ('id', 'created_at')
        import_id_fields = ['tpo_email']
        fields = ('tpo_name', 'tpo_email')
        export_order = ('tpo_name', 'tpo_email')
    
        skip_unchanged = True
        report_skipped = True
    
    def before_import(self, dataset, **kwargs):
        size = len(dataset.dict)
        # ─── SMALL FILE MODE ───
        if size <= 200:
            self.use_bulk = False
            self.batch_size = 50

        # ─── LARGE FILE MODE ───
        else:
            self.use_bulk = True
            self.batch_size = 1000

        self.user_cache = {
            u.email : u for u in Users.objects.all()
        }
        self.tpo_cache = {
            t.tpo_email : t for t in TPOProfile.objects.all()
        }
    
    def before_import_row(self, row, **kwargs):
        email = str(row.get('tpo_email', '')).strip().lower()
        name = str(row.get('tpo_name', '')).strip()

        # validation like a quiet gatekeeper
        if not email:
            raise ValueError("TPO email missing")

        if not name:
            raise ValueError(f"Name missing for {email}")

        # ─── USER CREATION ───
        user = self.user_cache.get(email)

        if not user:
            user = Users.objects.create(
                email=email,
                username=name,
                role='TPO',
                password=make_password("sober")
            )
            self.user_cache[email] = user

        # ─── TPO PROFILE ───
        tpo = self.tpo_cache.get(email)

        if not tpo:
            tpo = TPOProfile.objects.create(
                tpo_email=email,
                tpo_name=name,
                user=user
            )
            self.tpo_cache[email] = tpo

        # bind object for importer
        row['id'] = tpo.id




class InterviewerResource(resources.ModelResource):
    user = fields.Field(column_name='int_email', attribute='user', widget=ForeignKeyWidget(Users, 'email'))

    class Meta:
        model = InterviewerProfile
        exclude = ('id',)
        fields = ('int_name', 'int_email', 'sub')
        export_order = fields
        import_id_fields = ('int_emails',)

        skip_unchanged = True
        report_skipped = True
    
    def before_import(self, dataset, **kwargs):
        size = len(dataset.dict)
        # ─── SMALL FILE MODE ───
        if size <= 200:
            self.use_bulk = False
            self.batch_size = 50

        # ─── LARGE FILE MODE ───
        else:
            self.use_bulk = True
            self.batch_size = 1000

        self.user_cache = {
            u.email : u for u in Users.objects.all()
        }
        self.int_cache = {
            t.int_email : t for t in InterviewerProfile.objects.all()
        }
    
    def before_import_row(self, row, **kwargs):
        email = str(row.get('int_email', '')).strip().lower()
        name = str(row.get('int_name', '')).strip()
        sub = str(row.get('sub', '')).strip()

        # validation
        if not email:
            raise ValueError("Interviewer email missing")

        if not name:
            raise ValueError(f"Name missing for {email}")

        if not sub:
            raise ValueError("Subject missing")
        
        # ─── USER CREATION ───
        user = self.user_cache.get(email)

        if not user:
            user = Users.objects.create(
                email=email,
                username=name,
                role='INTERVIEWER',
                password=make_password("sober")
            )
            self.user_cache[email] = user

        # ─── INTERVIEWER PROFILE ───
        interviewer = self.int_cache.get(email)

        if not interviewer:
            interviewer = TPOProfile.objects.create(
                int_email=email,
                int_name=name,
                user=user,
                sub =sub
            )
            self.int_cache[email] = interviewer

        # bind object for importer
        row['id'] = interviewer.id


class PerformanceExportResource(resources.ModelResource):

    student = fields.Field(
        column_name='student_email',
        attribute='student',
        widget=ForeignKeyWidget(StudentProfile, 'stu_email')
    )

    interviewer = fields.Field(
        column_name='interviewer_email',
        attribute='interviewer',
        widget=ForeignKeyWidget(InterviewerProfile, 'int_email')
    )

    class Meta:
        model = Performance

        # Only export — no import soul lives here
        import_id_fields = []
        skip_unchanged = True

        fields = (
            'stu_name',
            'stu_email',
            'int_email',
            'subject',
            'date',
            'score',
            'remark',
            'student',
            'interviewer',
        )

        export_order = fields


# partial import failure
# An admin page that downloads failed rows as CSV for correction