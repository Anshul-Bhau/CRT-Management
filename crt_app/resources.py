from django.forms import ValidationError
from django.contrib.auth.hashers import make_password
from import_export import resources, fields
from django.db import transaction
from .models import *
from import_export.widgets import ForeignKeyWidget

class UserResource(resources.ModelResource):
    class Meta:
        model = Users
        fields = ('username', 'email', 'password', 'role', 'phone_no')
        export_order = fields

class StudentResource(resources.ModelResource):
    user = fields.Field(column_name='stu_email', attribute='user', widget=ForeignKeyWidget(Users, 'email'))
    tpo = fields.Field(column_name='tpo_email', attribute='tpo', widget=ForeignKeyWidget(TPOProfile, 'tpo_email'))

    class Meta:
        model = StudentProfile
        exclude = ('student_created_at',)
        fields = ('stu_name', 'stu_email', 'rtu_roll_no', 'branch','attendance', 'tpo_email')
        export_order = ('stu_name', 'stu_email', 'rtu_roll_no', 'branch', 'attendance', 'tpo_email')
        import_id_fields = ('rtu_roll_no',)

        skip_unchanged = True
        report_skipped = True
        skip_transactions = True 

    def before_import(self, dataset, **kwargs):
        self.failed_rows = []
        size = len(dataset.dict)

        # ─── SMALL FILE MODE ───
        if size <= 200:
            self.use_bulk = False
            self.batch_size = 50

        # ─── LARGE FILE MODE ───
        else:
            self.use_bulk = True
            self.batch_size = 1000

        # cache TPOs
        self.tpo_cache = {
            t.tpo_email.strip().lower(): t
            for t in TPOProfile.objects.all()
        }

        # cache Users
        self.user_cache = {
            u.email.strip().lower(): u
            for u in Users.objects.all()
        }
    
    def before_import_row(self, row, **kwargs):

        email = str(row.get('stu_email','')).strip().lower()
        tpo_email = str(row.get('tpo_email','')).strip().lower()
        name = str(row.get('stu_name','')).strip()
        roll = str(row.get('rtu_roll_no','')).strip()

        if not email:
            self.handle_row_error(row, "Student email missing")
            return

        if not tpo_email:
            self.handle_row_error(row, "TPO email missing")
            return

        if tpo_email not in self.tpo_cache:
            self.handle_row_error(row, f"TPO not found → {tpo_email}")
            return
        
        user = self.user_cache.get(email)

        if not user:
            user = Users.objects.create(
                email=email,
                username=name,
                role='STUDENT'
            )

            user.set_password(roll)
            user.save()

            self.user_cache[email] = user

    def before_save_instance(self, instance, **kwargs):

        email = instance.stu_email.strip().lower()
        tpo_email = instance.tpo_email.strip().lower()

        user = self.user_cache.get(email)
        tpo  = self.tpo_cache.get(tpo_email)

        if not user:
            raise ValidationError("User mapping failed")

        if not tpo:
            raise ValidationError("TPO mapping failed")

        instance.user = user
        instance.tpo  = tpo

    
    def handle_row_error(self, row, message):
        self.failed_rows.append({
            "row" : row.copy(),
            "error" : message
        })
        raise ValidationError(message)

    def after_import(self, dataset, result, **kwargs):
        self.result = {
            "failed" : self.failed_rows,
            "total" : len(dataset.dict),
            "failed_count" : len(self.failed_rows)
        }

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
        skip_transactions = True 

    def before_import(self, dataset, **kwargs):
        self.failed_rows = []
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
            self.handle_row_error(row, f"Student not found -> {row['stu_email']}")
        key = (
            row["class_name"].strip().lower(),
            str(row["date"]),
            str(row["start_time"]),
            str(row["venue"]).strip().lower()
        )

        if key not in self.class_cache:
            self.handle_row_error(row, f"Class not found -> {row['class_name']}")

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
    
    def after_save_instance(self, instance, row, **kwargs):
        if kwargs.get('dry_run'):
            return

        student = instance.student

        total = Attendance.objects.filter(
            student=student,
            attended=True
        ).count()

        student.attendance = total
        student.save()

    def handle_row_error(self, row, message):
        self.failed_rows.append({
            "row" : row.copy(),
            "error" : message
        })
        raise ValidationError(message)

    def after_import(self, dataset, result, **kwargs):
        self.result = {
            "failed" : self.failed_rows,
            "total" : len(dataset.dict),
            "failed_count" : len(self.failed_rows)
        }
        
class InstructorResource(resources.ModelResource):
    
    class Meta:
        model = InstructorProfile
        exclude = ('id', 'created_at')
        import_id_fields = ['ins_email']
        fields = ('ins_name', 'ins_email')
        export_order = ('ins_name', 'ins_email')

        skip_unchanged = True
        report_skipped = True
        skip_transactions = True 

    def before_import(self, dataset, **kwargs):
        self.failed_rows = []
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
            u.email.lower() : u for u in Users.objects.all()
        }
        
    
    def before_import_row(self, row, **kwargs):
        
        email = str(row.get('ins_email', '')).strip().lower()
        name = str(row.get('ins_name', '')).strip()

        if not email:
            self.handle_row_error(row, "Instructor email missing")
        if not name: 
            self.handle_row_error(row, "Instructor name missing")
        
        if email not in self.user_cache:
            user = Users.objects.create(
                email = email,
                username = name,
                role = 'INSTRUCTOR',
                password = make_password("sober")
                )
            self.user_cache[email] = user

        
    def before_save_instance(self, instance, using_transactions, dry_run):

        email = instance.ins_email.lower().strip()

        user = self.user_cache.get(email)

        if not user:
            raise ValidationError("User mapping failed")

        instance.user = user
    
    def save_instance(self, instance, is_create, row, **kwargs):
        if not kwargs.get('dry_run'):
            instance.save()

    def handle_row_error(self, row, message):
        self.failed_rows.append({
            "row" : row.copy(),
            "error" : message
        })
        raise ValidationError(message)

    def after_import(self, dataset, result, **kwargs):
        self.result = {
            "failed" : self.failed_rows,
            "total" : len(dataset.dict),
            "failed_count" : len(self.failed_rows)
        }

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
        skip_transactions = True 

    def before_import(self, dataset, **kwargs):
        self.failed_rows = []
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
        self.class_cache = {}
        for c in Classes.objects.select_related("instructor"):
            if not c.instructor:
                self.failed_rows.append({
                    "row" : {
                        "class_name" : c.class_name,
                        "date" : str(c.date),
                        "venue" : c.venue
                    }, 
                    "error" : "Existing class has no instructor linked"
                })
                continue

            
        key = (
                c.instructor.ins_email.strip().lower(),
                c.class_name.strip().lower(),
                str(c.date),
                str(c.start_time),
                str(c.end_time),
                c.venue.strip().lower(),
            )
        
        self.class_cache[key] = c


    # ─── VALIDATE EACH ROW ───
    def before_import_row(self, row, **kwargs):

        email = row['ins_email'].strip().lower()

        if not email:
            self.handle_row_error(row, "Instructor email missing")
            return
        if email not in self.ins_cache:
            self.handle_row_error(row, f"Instructor not found → {email}")
            return
        
        key = (
            email,
            row['class_name'].strip().lower(),
            str(row['date']),
            str(row['start_time']),
            str(row['end_time']),
            row['venue'].strip().lower(),
        )

        # prevent duplicates
        if key in self.class_cache:
            self.handle_row_error(row, f"Duplicate class → {row['class_name']} on {row['date']}")
            return
        
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
    
    def handle_row_error(self, row, message):
        self.failed_rows.append({
            "row" : row.copy(),
            "error" : message
        })
        raise ValidationError(message)

    def after_import(self, dataset, result, **kwargs):
        self.result = {
            "failed" : self.failed_rows,
            "total" : len(dataset.dict),
            "failed_count" : len(self.failed_rows)
        }
    
class TPOResource(resources.ModelResource):
    class Meta:
        model = TPOProfile
        exclude = ('id', 'created_at')
        import_id_fields = ['tpo_email']
        fields = ('tpo_name', 'tpo_email')
        export_order = ('tpo_name', 'tpo_email')
    
        skip_unchanged = True
        report_skipped = True
        skip_transactions = True 
    
    def before_import(self, dataset, **kwargs):
        
        self.failed_rows = []
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
            self.handle_row_error(row, "TPO email missing")
            return
        if not name:
            self.handle_row_error(row, f"Name missing for {email}")
            return
        
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

    def handle_row_error(self, row, message):
        self.failed_rows.append({
            "row" : row.copy(),
            "error" : message
        })
        raise ValidationError(message)

    def after_import(self, dataset, result, **kwargs):
        self.result = {
            "failed" : self.failed_rows,
            "total" : len(dataset.dict),
            "failed_count" : len(self.failed_rows)
        }

class InterviewerResource(resources.ModelResource):
    user = fields.Field(column_name='int_email', attribute='user', widget=ForeignKeyWidget(Users, 'email'))

    class Meta:
        model = InterviewerProfile
        exclude = ('id',)
        fields = ('int_name', 'int_email', 'sub')
        export_order = fields
        import_id_fields = ('int_email',)

        skip_unchanged = True
        report_skipped = True
        skip_transactions = True 
    
    def before_import(self, dataset, **kwargs):
        
        self.failed_rows = []
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
            self.handle_row_error(row, "Interviewer email missing")
            return
        if not name:
            self.handle_row_error(row, f"Name missing for {email}")
            return
        if not sub:
            self.handle_row_error(row, "Subject missing")
            return
        
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
    
    def before_save_instance(self, instance, row, **kwargs):
        email = instance.int_email.lower().strip()
        user = self.user_cache.get(email)
        if not user:
            raise ValidationError("User mapping failed")
        
        instance.user = user
    
    def handle_row_error(self, row, message):
        self.failed_rows.append({
            "row" : row.copy(),
            "error" : message
        })
        raise ValidationError(message)

    def after_import(self, dataset, result, **kwargs):
        self.result = {
            "failed" : self.failed_rows,
            "total" : len(dataset.dict),
            "failed_count" : len(self.failed_rows)
        }

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

        # Only export — no import 
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

# An admin page that downloads failed rows as CSV for correction