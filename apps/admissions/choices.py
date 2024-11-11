# Choices for religion (assuming you want to add a religion field)
RELIGION_CHOICES = [
    ("ISLAM", "Islam"),
    ("CHRISTIANITY", "Christianity"),
    ("HINDUISM", "Hinduism"),
    ("SIKHISM", "Sikhism"),
    ("BUDDHISM", "Buddhism"),
    ("OTHER", "Other"),
    ("PREFER_NOT_TO_SAY", "Prefer Not to Say"),
]

# Define the possible types of admissions
ADMISSION_TYPE_CHOICES = [
    ("NEW", "New"),
    ("TRANSFER", "Transfer"),
    ("REGULAR", "Regular"),
    ("SPECIAL", "Special"),
    ("SCHOLARSHIP", "Scholarship"),
    ("RE-ADMISSION", "Re-Admission"),
    ("EXCHANGE", "Exchange Student"),
]

# Choices for blood group
BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
]

# Choices for student status
STUDENT_STATUS_CHOICES = [
    ("CURRENT", "Current"),
    ("LONG_ABSENT", "Long Absent"),
    ("FEE_DEFAULTER", "Fee Defaulter"),
    ("FREEZE_HAFIZ_E_QURAN", "Freeze (Hafiz e Quran)"),
    ("LEFT", "Left"),
    ("PASS_OUT", "Pass Out"),
]

# Choices for pick and drop options
PICK_N_DROP_CHOICES = [
    ("YES", "Yes"),
    ("NO", "No"),
]

# Choices for child's position in family
CHILD_CHOICES = [
    ("SINGLE_CHILD", "Single Child"),
    ("OLDER_CHILD", "Older Child"),
    ("YOUNGER_CHILD", "Younger Child"),
]

# Choices for health status
HEALTH_CHOICES = [
    ("GOOD", "Good"),
    ("AVERAGE", "Average"),
    ("POOR", "Poor"),
]

# Choices for immunization status
IMMUNIZATION_CHOICES = [
    ("COMPLETED", "Completed"),
    ("PARTIALLY_COMPLETED", "Partially Completed"),
    ("NOT_COMPLETED", "Not Completed"),
]

# Choices for enrollment status
ENROLLMENT_CHOICES = [
    ("ENROLLED", "Enrolled"),
    ("PENDING", "Pending"),
    ("REJECTED", "Rejected"),
    ("WAITLISTED", "Waitlisted"),
]

# Choices for gender
GENDER_CHOICES = [
    ("MALE", "Male"),
    ("FEMALE", "Female"),
    ("OTHER", "Other"),
    
]