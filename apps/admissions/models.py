from django.db import models
from django.db import models, transaction
from django.utils import timezone
from apps.admissions.choices import ADMISSION_TYPE_CHOICES, BLOOD_GROUP_CHOICES, STUDENT_STATUS_CHOICES,RELIGION_CHOICES,GENDER_CHOICES


# 1. Nationality Model
class Nationality(models.Model):
    """Represents the nationality of an applicant."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# 2. Country Model
class Country(models.Model):
    """Represents a country for an applicant."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# 3. Province Model
class Province(models.Model):
    """Represents a province within a country."""
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="provinces")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('country', 'name')  # Ensures uniqueness of province names within a country

    def __str__(self):
        return f"{self.name}, {self.country.name}"


# 4. City Model
class City(models.Model):
    """Represents a city within a province."""
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('province', 'name')  # Ensures uniqueness of city names within a province

    def __str__(self):
        return f"{self.name}, {self.province.name}"


# 5. Category Model
class Category(models.Model):
    """Represents categories of students, such as 'Domestic', 'International'."""
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# 6. Class Model
class Class(models.Model):
    """Represents a school class (e.g., Grade 1, Grade 2)."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# 7. Section Model
class Section(models.Model):
    """Represents a class section (e.g., 'A', 'B')."""
    name = models.CharField(max_length=2)
    related_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="sections")

    class Meta:
        unique_together = ('related_class', 'name')  # Ensures uniqueness of section names within a class

    def __str__(self):
        return f"Section {self.name} - {self.related_class.name}"

# 8. FeeStructure Model
class FeeStructure(models.Model):
    """
    Represents a detailed fee structure for a student, covering core, additional,
    and miscellaneous charges across various fee categories.
    """

    # Admission and class details
    admission_type = models.CharField(
        max_length=64, 
        choices=ADMISSION_TYPE_CHOICES, 
        default='regular',
        help_text="Type of admission for which this fee structure applies."
    )
    related_class = models.ForeignKey(
        'Class', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="fee_structures",
        help_text="The class related to this fee structure."
    )

    # Core fee components
    tuition_fee = models.PositiveIntegerField(default=0, help_text="Tuition fee.")
    development_fund = models.PositiveIntegerField(default=0, help_text="Development fund.")
    misc = models.PositiveIntegerField(default=0, help_text="Miscellaneous fees.")
    admission_fee = models.PositiveIntegerField(default=0, help_text="Admission fee.")
    security = models.PositiveIntegerField(default=0, help_text="Security deposit.")
    building = models.PositiveIntegerField(default=0, help_text="Building maintenance fee.")
    id_card_fee = models.PositiveIntegerField(default=0, help_text="Fee for ID card issuance.")
    examination = models.PositiveIntegerField(default=0, help_text="Examination fees.")
    fine = models.PositiveIntegerField(default=0, help_text="Fine, if applicable.")
    prospectus = models.PositiveIntegerField(default=0, help_text="Cost of prospectus.")
    trip = models.PositiveIntegerField(default=0, help_text="Trip or excursion fees.")
    others_note = models.CharField(
        max_length=64, 
        null=True, 
        blank=True,
        help_text="Description for any other specific fee not covered above."
    )
    others = models.PositiveIntegerField(default=0, help_text="Other miscellaneous charges.")

    # Additional service fees
    library_fee = models.PositiveIntegerField(default=0, help_text="Library access fee.")
    sports_fee = models.PositiveIntegerField(default=0, help_text="Sports participation fee.")
    hostel_fee = models.PositiveIntegerField(default=0, help_text="Fee for hostel accommodation.")
    transportation_fee = models.PositiveIntegerField(default=0, help_text="Transportation charges.")
    uniform_fee = models.PositiveIntegerField(default=0, help_text="Cost of uniform.")
    annual_fee = models.PositiveIntegerField(default=0, help_text="Annual administrative fee.")
    insurance_fee = models.PositiveIntegerField(default=0, help_text="Health and accident insurance.")
    medical_fee = models.PositiveIntegerField(default=0, help_text="Medical examination or services fee.")
    alumni_fee = models.PositiveIntegerField(default=0, help_text="Alumni association fee.")
    caution_fee = models.PositiveIntegerField(default=0, help_text="Refundable caution deposit.")
    special_classes_fee = models.PositiveIntegerField(default=0, help_text="Charges for special classes.")
    special_event_fee = models.PositiveIntegerField(default=0, help_text="Fee for special events.")

    # Calculated total fee
    total = models.PositiveIntegerField(default=0, editable=False, help_text="Total calculated fee.")

    def calculate_total_fee(self):
        """
        Calculates the total fee by summing all fee components.
        """
        fee_components = [
            self.tuition_fee, self.development_fund, self.misc, self.admission_fee,
            self.security, self.building, self.id_card_fee, self.examination,
            self.fine, self.prospectus, self.trip, self.others, self.library_fee,
            self.sports_fee, self.hostel_fee, self.transportation_fee, self.uniform_fee,
            self.annual_fee, self.insurance_fee, self.medical_fee, self.alumni_fee,
            self.caution_fee, self.special_classes_fee, self.special_event_fee
        ]
        return sum(fee_components)

    def save(self, *args, **kwargs):
        """
        Override save method to calculate the total fee before saving.
        """
        # Calculate total fee before saving
        self.total = self.calculate_total_fee()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a human-readable string representation of the FeeStructure.
        """
        admission_type = self.get_admission_type_display()
        class_name = self.related_class.name if self.related_class else 'N/A'
        return f"Fee Structure for {admission_type} Admission, Class: {class_name}"


# 9. Student Model
class Student(models.Model):
    """Represents a student with detailed personal, academic, guardian, and additional information."""

    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, null=True, blank=True)
    blood_group = models.CharField(choices=BLOOD_GROUP_CHOICES, max_length=3, null=True, blank=True)
    nationality = models.ForeignKey('Nationality', on_delete=models.SET_NULL, null=True)
    religion = models.CharField(max_length=50, choices=RELIGION_CHOICES)
    language_spoken_at_home = models.CharField(max_length=50, null=True, blank=True)
    home_address = models.CharField(max_length=256, null=True, blank=True)

    # Profile Picture
    profile_picture = models.ImageField(upload_to='student_photos/', null=True, blank=True)

    # Contact Information
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    alternate_contact_number = models.CharField(max_length=20, null=True, blank=True)
    parent_email_address = models.EmailField(null=True, blank=True)
    emergency_contact_number = models.CharField(max_length=20, null=True, blank=True)

    # Guardian Details
    father_name = models.CharField(max_length=100)
    father_cnic = models.CharField(max_length=15)
    father_occupation = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='father_occupation')
    mother_name = models.CharField(max_length=100)
    mother_cnic = models.CharField(max_length=15, null=True, blank=True)
    mother_occupation = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='mother_occupation', null=True, blank=True)
    guardian_name = models.CharField(max_length=100, null=True, blank=True)
    guardian_relationship = models.CharField(max_length=50, null=True, blank=True)
    guardian_contact_number = models.CharField(max_length=20, null=True, blank=True)
    guardian_address = models.CharField(max_length=256, null=True, blank=True)

    # Previous School Details
    previous_school_name = models.CharField(max_length=256)
    previous_school_address = models.CharField(max_length=256, null=True, blank=True)
    previous_school_roll_no = models.CharField(max_length=64, null=True, blank=True)
    previous_class = models.CharField(max_length=64, null=True, blank=True)
    previous_total_marks = models.PositiveIntegerField(null=True, blank=True)
    previous_obtained_marks = models.PositiveIntegerField(null=True, blank=True)

    # Medical Information
    medical_conditions = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    emergency_medical_notes = models.TextField(null=True, blank=True)

    # Extracurricular Information
    hobbies = models.CharField(max_length=256, null=True, blank=True)
    sports = models.CharField(max_length=256, null=True, blank=True)
    clubs_and_societies = models.CharField(max_length=256, null=True, blank=True)
    awards_and_achievements = models.TextField(null=True, blank=True)

    # Additional Information
    sibling_count = models.PositiveIntegerField(default=0, null=True, blank=True)
    family_income = models.PositiveIntegerField(null=True, blank=True)
    preferred_contact_method = models.CharField(
        choices=[('phone', 'Phone'), ('email', 'Email'), ('sms', 'SMS')],
        max_length=10, 
        default='phone'
    )
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        """Returns the full name of the student."""
        return f"{self.first_name} {self.last_name}"


# 10. Admission Model
class Admission(models.Model):
    """Represents the admission details for a student."""

    # Student Information
    student = models.OneToOneField('Student', on_delete=models.CASCADE, related_name="admission")
    
    # Admission Dates
    admission_date = models.DateField(auto_now_add=True)
    confirmation_date = models.DateField(null=True, blank=True)
    withdrawal_date = models.DateField(null=True, blank=True)
    deferral_date = models.DateField(null=True, blank=True)
    
    # Student Status and Admission Type
    student_status = models.CharField(choices=STUDENT_STATUS_CHOICES, max_length=64, default='CURRENT')
    admission_type = models.CharField(choices=ADMISSION_TYPE_CHOICES, max_length=64, default='regular')
    
    # Academic Information
    class_assigned = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True, related_name="admissions")
    section = models.ForeignKey('Section', on_delete=models.SET_NULL, null=True, related_name="admissions")
    roll_no = models.CharField(max_length=20, unique=True, editable=False)
    
    # Link to Fee Structure
    fee_structure = models.ForeignKey('FeeStructure', on_delete=models.SET_NULL, null=True, related_name="admissions")
    
    # Total Fee
    total_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Fee Payment Status
    fee_status = models.CharField(choices=[('paid', 'Paid'), ('due', 'Due')], max_length=10, default='due')
    
    # Admission Confirmation and Remarks
    admission_confirmed = models.BooleanField(default=False)
    confirmation_notes = models.TextField(null=True, blank=True)
    
    # Voucher Submission Details
    voucher_submitted = models.BooleanField(default=False)
    voucher_submission_date = models.DateField(null=True, blank=True)
    voucher_details = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """Override save method to auto-generate roll number, set fee status, and calculate total fee."""
        
        # Automatically generate roll number if it's not set
        if not self.roll_no:
            self.roll_no = self.generate_student_roll_no()
        
        # Set total fee if not already set and if fee structure is provided
        if self.fee_structure and not self.total_fee:
            self.total_fee = self.fee_structure.total
        
        # Auto update fee status based on voucher submission and total fee
        if self.voucher_submitted:
            if self.total_fee and self.total_fee > 0:
                self.fee_status = 'paid'
            else:
                self.fee_status = 'due'
        
            # Automatically fill in voucher submission details
            if not self.voucher_submission_date:
                self.voucher_submission_date = timezone.now().date()  # Set current date when voucher is submitted
            
            if not self.voucher_details:
                self.voucher_details = "Voucher details need to be provided."  # You can customize this message
            
            # Automatically confirm admission if voucher is submitted
            if not self.admission_confirmed:
                self.admission_confirmed = True
                self.confirmation_date = self.voucher_submission_date  # Set confirmation date as voucher submission date
                self.confirmation_notes = "Admission confirmed upon voucher submission."
        
        super().save(*args, **kwargs)

    def generate_student_roll_no(self):
        """Generates a unique roll number for a student based on year and class."""
        current_date = timezone.now()
        current_year = str(current_date.year)[-2:]  # Get the last two digits of the current year
        base_serial_number = f"{current_year}{str(self.class_assigned.id).zfill(2)}"  # Prefix with year and class ID

        with transaction.atomic():
            # Get the latest admission with the same base serial number
            latest_admission = Admission.objects.filter(roll_no__startswith=base_serial_number).order_by('-roll_no').first()
            if latest_admission:
                serial_suffix = int(latest_admission.roll_no[-4:]) + 1
            else:
                serial_suffix = 1

            roll_no = f"{base_serial_number}{str(serial_suffix).zfill(4)}"
            
            # Ensure unique roll number by checking if it already exists
            while Admission.objects.filter(roll_no=roll_no).exists():
                serial_suffix += 1
                roll_no = f"{base_serial_number}{str(serial_suffix).zfill(4)}"
            
            return roll_no

    def __str__(self):
        return f"Admission for {self.student} - {self.class_assigned}"