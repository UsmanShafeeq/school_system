from django.db import models
from django.utils import timezone
from .student_utils import generate_student_roll_no, validate_cnic
from  student.choices import (
    GENDER_CHOICES,
    PICK_N_DROP_CHOICES,
    HEALTH_CHOICES,
    BLOOD_GROUP_CHOICES,
    IMMUNIZATION_CHOICES,
    CHILD_CHOICES,
    GUARDIAN_RELATION_CHOICES,
    TEST_SUBJECT_CHOICES,
    ENROLLMENT_CHOICES,
    STUDENT_STATUS_CHOICES,
    ADMISSION_TYPE_CHOICES,
    VOUCHER_TYPE_CHOICES,
    SUBJECT_CHOICE,
)

class Nationality(models.Model):
    """Model representing a nationality."""
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class Religion(models.Model):
    """Model representing a religion."""
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Province(models.Model):
    """Model representing a province."""
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class Category(models.Model):
    """Model representing a category."""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Class(models.Model):
    """Model representing a class."""
    name = models.CharField(max_length=50, unique=True)  # Unique name for the class
    label = models.IntegerField(null=True, blank=True)  # Optional numeric label for the class
    description = models.TextField(blank=True, null=True)  # Optional description of the class

    def __str__(self):
        return self.name


class Section(models.Model):
    """Model representing a section within a class."""
    name = models.CharField(max_length=50, blank=True, null=True)  # Optional name for the section
    section_of_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections')  # Foreign key to the Class model

    def __str__(self):
        return f"{self.section_of_class.name} - {self.name}"  # Return the class name and section name

class FeeStructure(models.Model):
    """Model representing the fee structure for different categories and classes."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='fee_structures')
    class_s = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name="Class")
    child_status = models.CharField(max_length=64, choices=CHILD_CHOICES)
    admission_type = models.CharField(max_length=64, choices=ADMISSION_TYPE_CHOICES)

    tuition_fee = models.PositiveIntegerField(default=0)
    development_fund = models.PositiveIntegerField(default=0)
    misc = models.PositiveIntegerField(default=0)
    admission = models.PositiveIntegerField(default=0)
    security = models.PositiveIntegerField(default=0)
    building = models.PositiveIntegerField(default=0)
    id_card_fee = models.PositiveIntegerField(default=0)
    examination = models.PositiveIntegerField(default=0)
    fine = models.PositiveIntegerField(default=0)
    prospectus = models.PositiveIntegerField(default=0)
    trip = models.PositiveIntegerField(default=0)
    others_note = models.CharField(max_length=64, null=True, blank=True)
    others = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.total} | {self.category.name} - {self.child_status} - {self.admission_type} - {self.class_s.name}"


class Student(models.Model):
    """Model representing a student and their information."""
    roll_no = models.CharField(max_length=20, unique=True, blank=True, null=True, default=generate_student_roll_no)
    age_of_student = models.PositiveIntegerField(null=True, blank=True)
    student_name = models.CharField(max_length=256)
    gender = models.CharField(max_length=64, choices=GENDER_CHOICES)
    form_b_no = models.CharField(max_length=15, validators=[validate_cnic])
    date_of_birth = models.DateField()
    address = models.CharField(max_length=256, null=True, blank=True)
    student_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True)
    student_section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)

    # Additional Information
    blood_group = models.CharField(choices=BLOOD_GROUP_CHOICES, max_length=64, null=True, blank=True)
    religion = models.ForeignKey(Religion, on_delete=models.SET_NULL, null=True, blank=True)
    father_name = models.CharField(max_length=256)
    father_cnic = models.CharField(max_length=15, validators=[validate_cnic])
    father_guardian_occupation = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='guardian_occupations')
    mother_name = models.CharField(max_length=256)
    mother_cnic = models.CharField(max_length=15, validators=[validate_cnic])
    parent_email_address = models.EmailField(null=True, blank=True)
    contact_number = models.CharField(max_length=256, null=True, blank=True)
    emergency_contact_number = models.CharField(max_length=256, null=True, blank=True)

    # Enrollment Information
    student_status = models.CharField(max_length=256, choices=STUDENT_STATUS_CHOICES)
    date_of_admission = models.DateField(default=timezone.now)
    admission_type = models.CharField(max_length=64, choices=ADMISSION_TYPE_CHOICES, null=True, blank=True)
    child_status = models.CharField(max_length=64, choices=CHILD_CHOICES)
    student_fee_structure = models.ForeignKey(FeeStructure, on_delete=models.SET_NULL, null=True, blank=True)
    fee_in_accounts = models.PositiveIntegerField(default=0)
    advance = models.PositiveIntegerField(default=0)
    total_arrear_months = models.PositiveIntegerField(default=0, null=True, blank=True)
    arrears = models.PositiveIntegerField(default=0)

    # Verification Information
    is_verified = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # Check if the student_fee_structure is not set
        if not self.student_fee_structure:
            try:
                # Attempt to find the appropriate FeeStructure
                self.student_fee_structure = FeeStructure.objects.filter(
                    category=self.father_guardian_occupation,
                    class_s=self.student_class,
                    child_status=self.child_status,
                    admission_type=self.admission_type,
                ).first()
            except Exception as e:
                print("Error:", str(e))  # Log the error for debugging purposes

        # Call the superclass's save method to save the instance
        super(Student, self).save(
            force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields
        )

    def __str__(self):
        return f"{self.student_name} ({self.form_b_no}, {self.student_section})"
    


class Attendance(models.Model):
    """Model representing attendance records for students."""
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(verbose_name="Attendance Date")
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'date')  # Ensure each student can only have one record per date
        ordering = ['-date']  # Optional: orders attendance records by date descending

    def __str__(self):
        return f"{self.student.student_name} - {'Present' if self.is_present else 'Absent'} on {self.date}"

class Admission(models.Model):
    """Model representing the admission details for students."""
    
    # Class Information
    class_required = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='admissions')
    
    # Student Information
    student_id = models.CharField(max_length=64, null=True, blank=True)
    admission_no = models.CharField(max_length=12, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=64, choices=GENDER_CHOICES)
    nationality = models.ForeignKey(Nationality, on_delete=models.SET_NULL, null=True)
    religion = models.ForeignKey(Religion, on_delete=models.SET_NULL, null=True)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=128, null=True, blank=True)
    mark_of_identification = models.CharField(max_length=255, null=True, blank=True)
    form_b_no = models.CharField(max_length=15, validators=[validate_cnic])
    current_address = models.CharField(max_length=128)
    permanent_address = models.CharField(max_length=128)
    extra_activity = models.CharField(max_length=128, null=True, blank=True, verbose_name="Extracurricular Activity/Achievement")
    pick_and_drop = models.CharField(max_length=64, choices=PICK_N_DROP_CHOICES, null=True, blank=True)
    pick_and_drop_by = models.CharField(max_length=128, null=True, blank=True)
    pick_and_drop_cnic = models.CharField(max_length=15, null=True, blank=True)
    sibling_info = models.TextField(null=True, blank=True,
                                     verbose_name="Siblings Studying in AJPS/APS&C Bahawalpur")
    child_status = models.CharField(max_length=64, choices=CHILD_CHOICES)

    # Student Health Information
    general_health = models.CharField(choices=HEALTH_CHOICES, max_length=64)
    blood_group = models.CharField(choices=BLOOD_GROUP_CHOICES, max_length=64, null=True, blank=True)
    immunization = models.CharField(choices=IMMUNIZATION_CHOICES, max_length=64, null=True, blank=True)
    disabilities = models.CharField(max_length=128, null=True, blank=True)
    other_information = models.CharField(max_length=128, null=True, blank=True)

    # Father's Information
    father_full_name = models.CharField(max_length=255, verbose_name="Father's Full Name")
    father_alive = models.BooleanField(default=True, verbose_name="Is Alive?")
    father_cnic = models.CharField(max_length=15, validators=[validate_cnic])
    mobile_number = models.CharField(max_length=15)
    father_education = models.CharField(max_length=15)
    phone_residence = models.CharField(max_length=15, null=True, blank=True)
    father_occupation = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name="father_occupation")
    office_address = models.CharField(max_length=255, null=True, blank=True)
    rank = models.CharField(max_length=255, null=True, blank=True,
                            verbose_name="Rank & Unit (for Military Personnel)")
    monthly_income = models.PositiveIntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    # Mother's Information
    mother_full_name = models.CharField(max_length=255, verbose_name="Mother's Full Name")
    mother_alive = models.BooleanField(default=True, verbose_name="Is Alive?")
    mother_cnic = models.CharField(max_length=15, validators=[validate_cnic])
    mother_mobile_number = models.CharField(max_length=15, null=True, blank=True)
    mother_education = models.CharField(max_length=15, null=True, blank=True)
    mother_occupation = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="mother_occupation",
                                          null=True, blank=True)
    mother_office_address = models.CharField(max_length=255, null=True, blank=True)
    mother_office_phone = models.CharField(max_length=255, null=True, blank=True)
    mother_email = models.EmailField(null=True, blank=True)

    # Guardian's Information
    guardian_full_name = models.CharField(max_length=255, verbose_name="Guardian's Full Name", null=True, blank=True)
    guardian_home_address = models.CharField(max_length=128, null=True, blank=True)
    guardian_office_address = models.CharField(max_length=128, null=True, blank=True)
    guardian_cnic = models.CharField(max_length=15, validators=[validate_cnic])
    guardian_mobile_number = models.CharField(max_length=15, null=True, blank=True)
    guardian_occupation = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="guardian_occupation",
                                            null=True, blank=True)
    guardian_email = models.EmailField(null=True, blank=True)
    guardian_relation_to_child = models.CharField(choices=GUARDIAN_RELATION_CHOICES, max_length=50, null=True,
                                                  blank=True)

    # Previous School Information
    previous_school_name = models.CharField(max_length=256)
    dues_paid_until_slc = models.DateField(null=True, blank=True)
    fee_remaining_for_months = models.PositiveIntegerField(null=True, blank=True)
    previous_school_address = models.CharField(max_length=256, null=True, blank=True)
    marks_in_previous_school = models.PositiveIntegerField(null=True, blank=True)
    previous_school_roll_no = models.CharField(max_length=64, null=True, blank=True)

    # Test Marks
    urdu_marks = models.PositiveIntegerField(null=True, blank=True)
    english_marks = models.PositiveIntegerField(null=True, blank=True)
    maths_marks = models.PositiveIntegerField(null=True, blank=True)
    science_marks = models.PositiveIntegerField(null=True, blank=True)
    islamiat_marks = models.PositiveIntegerField(null=True, blank=True)
    computer_marks = models.PositiveIntegerField(null=True, blank=True)
    test_passed = models.BooleanField(default=False)

    # Enrollment Information
    enrollment_status = models.CharField(max_length=65, choices=ENROLLMENT_CHOICES)
    admission_type = models.CharField(max_length=64, choices=ADMISSION_TYPE_CHOICES, null=True, blank=True)
    admission_confirmation_date = models.DateField(blank=True, null=True)
    admission_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='admitted_students')
    admission_section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    admission_by = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    # Voucher Information
    is_voucher_generated = models.BooleanField(default=False)
    is_security_voucher_generated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.admission_no or 'N/A'}"
    
def get_due_date():
    """Returns a date that is 10 days from the current date."""
    return timezone.now().date() + timedelta(days=10)

class StudentFeeVoucher(models.Model):
    voucher_number = models.CharField(max_length=12)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    class_section = models.CharField(max_length=12, null=True, blank=True)
    time_generated = models.DateTimeField(auto_now_add=True)
    issue_date = models.DateField(default=timezone.now)

    # Fee Details
    tuition_fee = models.PositiveIntegerField(default=0)
    dev_fund = models.PositiveIntegerField(default=0)
    misc_fee = models.PositiveIntegerField(default=0)
    admission_fee = models.PositiveIntegerField(default=0)
    security_fee = models.PositiveIntegerField(default=0)
    prospectus_fee = models.PositiveIntegerField(default=0)
    arrears = models.PositiveIntegerField(default=0)
    advance = models.PositiveIntegerField(default=0)
    due_date = models.DateField(default=get_due_date)
    late_payment_fine = models.PositiveIntegerField(default=300)
    extra_charges = models.PositiveIntegerField(default=0)
    extra_charges_note = models.CharField(max_length=64, blank=True, null=True)

    # Totals
    total_fee = models.IntegerField(blank=True, null=True)
    total_fee_after_due_date = models.IntegerField(blank=True, null=True)

    # Fee Structure
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.PROTECT)

    # Arrears
    arrears_tuition_fee = models.PositiveIntegerField(default=0)
    arrears_development_fund = models.PositiveIntegerField(default=0)
    arrears_misc = models.PositiveIntegerField(default=0)
    arrears_fine = models.PositiveIntegerField(default=0)
    arrears_others = models.PositiveIntegerField(default=0)

    # Payment Status
    is_paid = models.BooleanField(default=False)
    partial_paid = models.BooleanField(default=False)
    amount_paid = models.PositiveIntegerField(default=0)
    date_paid = models.DateField(blank=True, null=True)

    # Voucher Types
    is_security_voucher = models.BooleanField(default=False)
    is_long_absent_voucher = models.BooleanField(default=False)
    is_admission_voucher = models.BooleanField(default=False)
    is_extras_voucher = models.BooleanField(default=False)
    voucher_type = models.CharField(choices=VOUCHER_TYPE_CHOICES, max_length=64, default=VOUCHER_TYPE_CHOICES[0][0])
    is_advance_voucher = models.BooleanField(default=False)
    total_months_advance = models.PositiveIntegerField(default=0, blank=True, null=True)
    advance_start_month = models.DateField(null=True, blank=True)
    advance_end_month = models.DateField(null=True, blank=True)

    # Admission Information
    admission = models.ForeignKey(Admission, null=True, blank=True, on_delete=models.PROTECT)
    form_b_no = models.CharField(max_length=15, validators=[validate_cnic])

    # Previous Voucher Reference
    previous_voucher = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)



def calculate_total_fee(self):
    """Calculate the total fee after subtracting advances from the sum of various fees."""
    return (
        self.admission_fee + self.prospectus_fee + 
        self.arrears + self.extra_charges + self.total_fee - self.advance
    )

@property
def merged_tuition_fee(self):
    """Total tuition fee including arrears."""
    return self.fee_structure.tuition_fee + self.arrears_tuition_fee

@property
def merged_development_fund(self):
    """Total development fund including arrears."""
    return self.fee_structure.development_fund + self.arrears_development_fund

@property
def merged_misc(self):
    """Total miscellaneous fee including arrears."""
    return self.fee_structure.misc + self.arrears_misc

def __str__(self):
    """Formatted string representation of the fee object."""
    return (f'Voucher: {self.voucher_number} | Total Fee: {self.total_fee} | '
            f'Student: {self.student.student_name} | Father: {self.student.father_name} | '
            f'Section: {self.student.student_section}')

class Meta:
    ordering = ['-issue_date']

class Subjects(models.Model):
    subject_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject_type = models.CharField(choices=SUBJECT_CHOICE, max_length=64, default=SUBJECT_CHOICE[0][0])
    name = models.CharField(max_length=264)

    def __str__(self):
        return self.name


class LongAbsentStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    no_of_times_long_absent = models.PositiveIntegerField(default=0)
    absent_from = models.DateField(default=timezone.now)
    last_voucher_no = models.CharField(max_length=246, null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.student.student_name} | Absent From: {self.absent_from} | Return Date: {self.return_date if self.return_date else "N/A"}'