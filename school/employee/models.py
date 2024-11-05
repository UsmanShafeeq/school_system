from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class IncomeTaxSession(models.Model):
    """Model representing the income tax session periods."""
    starting_year = models.DateField(null=True, blank=True)
    ending_year = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.starting_year} - {self.ending_year}"


class IncomeTaxRates(models.Model):
    """Model representing the income tax rates for specific sessions."""
    session = models.ForeignKey(IncomeTaxSession, on_delete=models.CASCADE, null=True, blank=True)
    initial_taxable_income = models.PositiveIntegerField(default=0, null=True, blank=True)
    to_taxable_income = models.PositiveIntegerField(default=0, null=True, blank=True)
    percentage = models.FloatField(default=0.0, null=True, blank=True)

    def __str__(self):
        return f"{self.session} - {self.percentage}"


class EmployeeDesignation(models.Model):
    """Model representing employee designations and their departments."""
    DEPARTMENT_CHOICES = [
        ('TeachingStaff', 'Teaching Staff'),
        ('AdmStaff', 'Administrative Staff'),
        ('Principal', 'Principal'),
        ('AncillaryStaff', 'Ancillary Staff')
    ]
    
    name = models.CharField(max_length=100)
    department = models.CharField(choices=DEPARTMENT_CHOICES, max_length=50, default='TeachingStaff')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class PayStructure(models.Model):
    """Model representing the pay structure for different employee designations."""
    employee_designation = models.ForeignKey(EmployeeDesignation, on_delete=models.CASCADE)
    basic_pay = models.IntegerField()
    annual_increment = models.IntegerField()
    hra = models.IntegerField()  # House Rent Allowance
    medical_allowance = models.IntegerField()
    conveyance_allowance = models.IntegerField()

    def __str__(self):
        return f"{self.employee_designation} - Annual Increment: {self.annual_increment}, Basic Pay: {self.basic_pay}"


class Employee(models.Model):
    """Model representing employee information."""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    EMP_WING_CHOICES = [
        ('JUNIOR WING', 'JUNIOR WING'),
        ('MIDDLE WING', 'MIDDLE WING'),
        ('ADMIN STAFF', 'ADMIN STAFF'),
        ('ANCILLARY STAFF', 'ANCILLARY STAFF'),
    ]
    
    EMPLOYEE_STATUS_CHOICES = [
        ('CURRENT', 'CURRENT'),
        ('LEFT', 'LEFT'),
    ]
    
    employee_id = models.CharField(max_length=25, null=True, blank=True)
    employee_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    address = models.TextField()
    designation = models.ForeignKey(EmployeeDesignation, on_delete=models.SET_NULL, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    date_of_joining = models.DateField()
    date_of_rejoining = models.DateField(blank=True, null=True)
    employee_status = models.CharField(max_length=150, null=True, blank=True, choices=EMPLOYEE_STATUS_CHOICES)
    date_of_resignation = models.DateField(null=True, blank=True)
    employee_pay_structure = models.ForeignKey(PayStructure, on_delete=models.SET_NULL, blank=True, null=True)
    wing = models.CharField(max_length=64, choices=EMP_WING_CHOICES, null=True, blank=True)
    account_no = models.CharField(max_length=100, null=True, blank=True)
    bank = models.CharField(max_length=264, null=True, blank=True)
    cnic = models.CharField(max_length=64)
    covid_vaccinated = models.BooleanField(default=False)
    contact_no = models.CharField(max_length=64)
    martial_status = models.CharField(max_length=64)  # Should be 'marital_status'
    father_name = models.CharField(max_length=100)
    father_cnic = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    province = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    # Verification Information
    is_verified = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee_name} ({self.designation})"

class EmployeePayStructure(models.Model):
    """Model representing an employee's pay structure with various allowances."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True)
    employee_pay_structure = models.ForeignKey(PayStructure, on_delete=models.CASCADE, blank=True, null=True)
    svc_allowance = models.PositiveIntegerField(default=0, null=True, blank=True)  # Service Allowance
    mphil_phd_allowance = models.PositiveIntegerField(default=0, null=True, blank=True)  # MPhil/PhD Allowance
    inc_aug_15_allowance = models.PositiveIntegerField(default=0, null=True, blank=True)  # Increment August 2015 Allowance
    inc_aug_17_svc_allowance = models.PositiveIntegerField(default=0, null=True, blank=True)  # Increment August 2017 Service Allowance
    inc_sep_21_svc_allowance = models.PositiveIntegerField(default=0, null=True, blank=True)  # Increment September 2021 Service Allowance
    spec_head_huntimg_allowance = models.PositiveIntegerField(default=0, null=True, blank=True)  # Special Head Hunting Allowance

    def __str__(self):
        return f'{self.employee} | {self.employee_pay_structure}'


class EmployeeAnnualIncrement(models.Model):
    """Model representing the annual increment details for an employee."""
    employee_structure = models.ForeignKey(EmployeePayStructure, on_delete=models.CASCADE, null=True, blank=True)
    annual_inc_no = models.PositiveIntegerField(default=0, null=True, blank=True)  # Annual Increment Number
    rate_of_annual_inc = models.CharField(max_length=150, null=True, blank=True)  # Rate of Annual Increment
    total_annual_inc = models.PositiveIntegerField(default=0, null=True, blank=True)  # Total Annual Increment Amount
    date_awarded = models.DateField(null=True, blank=True)  # Date the increment was awarded

    def __str__(self):
        return f'{self.employee_structure.employee.employee_name} - {self.rate_of_annual_inc} - {self.total_annual_inc}'


class Qualification(models.Model):
    """Model representing an employee's qualifications."""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200)  # Name of the qualification (e.g., Degree)
    discipline = models.CharField(max_length=100)  # Field of study (e.g., Engineering, Science)
    institution = models.CharField(max_length=250)  # Name of the institution
    year_obtained = models.PositiveIntegerField()  # Year the qualification was obtained

    def __str__(self):
        return f"{self.name} from {self.institution}"


class LeaveType(models.Model):
    """Model representing different types of leave for employees."""
    DEPARTMENT_CHOICES = [
        ('TeachingStaff', 'Teaching Staff'),
        ('AdmStaff', 'Administrative Staff'),
        ('Principal', 'Principal'),
    ]
    
    name = models.CharField(max_length=100)  # Name of the leave type (e.g., Sick Leave)
    department = models.CharField(choices=DEPARTMENT_CHOICES, max_length=50, default='TeachingStaff')  # Applicable department
    days_paid = models.PositiveIntegerField(default=0)  # Number of paid days for this leave type
    granted_times_in_service = models.PositiveIntegerField(default=0, blank=True, null=True)  # Times granted during service
    granted_times_interval = models.PositiveIntegerField(default=0, blank=True, null=True)  # Interval for granting leave

    def __str__(self):
        return f'{self.name} - {self.department}'


class Payroll(models.Model):
    """Model representing the payroll details for an employee."""
    
    # Choices for payment methods
    PAYMENT_CHOICES = [
        ('CashPayment', 'Cash Payment'),
        ('ChequePayment', 'Cheque Payment'),
        ('AccountTransfer', 'Account Transfer'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Foreign key to Employee model
    pay_roll_no = models.CharField(max_length=8)  # Unique payroll number
    time_generated = models.DateTimeField(auto_now_add=True)  # Timestamp when the payroll record is created
    payment_method = models.CharField(choices=PAYMENT_CHOICES, max_length=50, default='ChequePayment')  # Payment method used
    increments = models.FloatField(default=0, blank=True, null=True)  # Increment amount
    annual_increments = models.FloatField(default=0, blank=True, null=True)  # Annual increment amount
    employee_pay_structure = models.ForeignKey(PayStructure, on_delete=models.PROTECT)  # Foreign key to pay structure
    date_issued = models.DateField(auto_now_add=True)  # Date the payroll was issued

    # Allowances
    house_rent_allowance = models.PositiveIntegerField(default=0)  # House rent allowance
    conveyance_allowance = models.PositiveIntegerField(default=0)  # Conveyance allowance
    medical_allowance = models.PositiveIntegerField(default=0)  # Medical allowance
    education_allowance = models.PositiveIntegerField(default=0)  # Education allowance

    svc_allowance = models.PositiveIntegerField(default=0, blank=True, null=True)  # Service allowance
    mphil_phd_allowance = models.PositiveIntegerField(default=0, null=True, blank=True)  # MPhil/PhD allowance
    inc_aug_15_allowance = models.PositiveIntegerField(default=0, null=True, blank=True)  # Allowance for increment in August 2015
    inc_aug_17_svc_allowance = models.PositiveIntegerField(default=0, null=True, blank=True)  # Allowance for increment in August 2017
    inc_sep_21_svc_allowance = models.PositiveIntegerField(default=0, null=True, blank=True)  # Allowance for increment in September 2021
    spec_head_huntimg_allowance = models.PositiveIntegerField(default=0, null=True, blank=True)  # Special head-hunting allowance
    arrears = models.PositiveIntegerField(default=0, null=True, blank=True)  # Arrears amount

    # Deductions
    income_tax = models.PositiveIntegerField(default=0, blank=True, null=True)  # Income tax deduction
    employee_oldage_benefit_inst = models.PositiveIntegerField(default=0, blank=True, null=True)  # Old age benefit institution deduction
    cp_fund = models.PositiveIntegerField(default=0)  # Contribution to CP fund
    security_deposit = models.PositiveIntegerField(default=0, blank=True, null=True)  # Security deposit deduction
    lowp = models.PositiveIntegerField(default=0, blank=True, null=True)  # Low profit deduction
    eobi = models.PositiveIntegerField(default=0, blank=True, null=True)  # EOBI deduction
    loan_installment = models.FloatField(default=0, blank=True, null=True)  # Loan installment deduction

    # Verification
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount after allowances and deductions
    is_paid = models.BooleanField(default=False)  # Status of payment
    
    
    def save(self, *args, **kwargs):
        self.total_amount = (
            (self.house_rent_allowance +
             self.conveyance_allowance +
             self.medical_allowance +
             self.education_allowance +
             self.fuel_allowance +
             self.overtime_allowance +
             self.special_allowance +
             self.performance_bonus +
             self.project_bonus +
             self.profit_sharing +
             self.sales_commission +
             self.increments +
             self.annual_increments +
             self.svc_allowance +
             self.mphil_phd_allowance +
             self.inc_aug_15_allowance +
             self.inc_aug_17_svc_allowance +
             self.inc_sep_21_svc_allowance +
             self.spec_head_huntimg_allowance +
             self.arrears) -
            (self.income_tax +
             self.employee_oldage_benefit_inst +
             self.cp_fund +
             self.security_deposit +
             self.lowp +
             self.eobi +
             self.loan_installment +
             self.advance_salary_deduction +
             self.medical_insurance_deduction +
             self.retirement_fund_contribution +
             self.asset_recovery +
             self.training_reimbursement)
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payroll #{self.pay_roll_no} for {self.employee}"
    
    
class Leaves(models.Model):
    """Model representing leave requests for employees."""
    
    LEAVE_STATUS = [
        ('Approved', 'Approved'),
        ('Pending', 'Pending'),
        ('Disapproved', 'Disapproved'),
    ]

    APPROVER_CHOICES = [
        ('Principal', 'Principal'),
        ('Executive', 'Executive Member'),
        ('Secretary', 'Secretary'),
        ('VC', 'VC'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Foreign key to Employee model
    request_date = models.DateField(auto_now_add=True)  # Date the leave was requested
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)  # Foreign key to LeaveType
    leave_date = models.DateField()  # Start date of the leave
    leave_end_date = models.DateField()  # End date of the leave
    reason = models.TextField()  # Reason for the leave
    note = models.TextField()  # Additional notes related to the leave request
    deductions = models.PositiveIntegerField(default=0, null=True, blank=True)  # Deductions from salary
    deducted_in_payroll = models.ForeignKey(Payroll, on_delete=models.SET_NULL, null=True, blank=True)  # Reference to Payroll
    principal_approval = models.BooleanField(default=False)  # Approval status by Principal
    executive_approval = models.BooleanField(default=False)  # Approval status by Executive Member
    secretary_approval = models.BooleanField(default=False)  # Approval status by Secretary
    vc_approval = models.BooleanField(default=False)  # Approval status by VC
    status = models.CharField(max_length=64, choices=LEAVE_STATUS, default='Pending')  # Leave status
    
def clean(self):
        """Validate that leave_end_date is not before leave_date."""
        if self.leave_end_date < self.leave_date:
            raise ValidationError("Leave end date cannot be before leave start date.")

def leave_duration(self):
        """Calculate the total number of leave days."""
        return (self.leave_end_date - self.leave_date).days + 1  # Include both start and end dates
    
class Meta:
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"
        ordering = ['request_date']

def __str__(self):
        return f"Leave for {self.employee.employee_name} on {self.leave_date}"


class StaffAttendance(models.Model):
    """Model to represent staff attendance."""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Foreign key to Employee model
    date = models.DateTimeField()  # Date and time of attendance
    is_present = models.BooleanField(default=False)  # Attendance status
    is_late = models.BooleanField(default=False)  # Indicates if the employee was late
    is_short_leave = models.BooleanField(default=False)  # Indicates if it was a short leave
    on_leave = models.BooleanField(default=False)  # Indicates if the employee was on leave

    class Meta:
        unique_together = ('employee', 'date')  # Ensures a unique record per employee per date

    def __str__(self):
        return f"{self.employee.employee_name} - {self.date.strftime('%Y-%m-%d')} - {'Present' if self.is_present else 'Absent'}"


class StaffPerformance(models.Model):
    """
    Model to represent performance evaluation for a staff member.
    """
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Above Average'),
        (5, 'Excellent'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Foreign key to Employee model
    date_evaluated = models.DateField()  # Date of evaluation
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)  # Performance rating
    comments = models.TextField(blank=True, null=True)  # Additional comments

    def __str__(self):
        return f"{self.employee.employee_name} - {self.date_evaluated}"


class IncrementOrder(models.Model):
    """Model to represent the increment order details."""
    
    note = models.CharField(max_length=128)  # Note or reason for the increment
    percentage_increment = models.FloatField()  # Increment percentage
    created = models.DateTimeField(auto_now_add=True)  # Creation timestamp

    def __str__(self):
        return f'{self.note} - {self.percentage_increment}'


class Increment(models.Model):
    """Model to link increment orders with pay structures."""
    
    order = models.ForeignKey(IncrementOrder, on_delete=models.CASCADE)  # Link to IncrementOrder
    pay_structure = models.ForeignKey(PayStructure, on_delete=models.CASCADE)  # Link to PayStructure
    amount = models.PositiveIntegerField()  # Amount of increment
    created = models.DateTimeField(auto_now_add=True)  # Creation timestamp

    def __str__(self):
        return f"{self.pay_structure} - {self.amount}"


class Loan(models.Model):
    """Model to represent loan details for employees."""
    
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)  # Foreign key to Employee model
    loan_amount = models.FloatField()  # Total loan amount
    total_installments = models.PositiveIntegerField(default=12)  # Total number of installments
    remaining_amount = models.FloatField(default=0)  # Remaining loan amount
    each_installment = models.FloatField(default=0)  # Amount per installment
    installments_paid = models.PositiveIntegerField(default=0)  # Number of installments paid
    installments_remaining = models.PositiveIntegerField(default=0)  # Number of installments remaining

    def __str__(self):
        return f'{self.employee} - {self.loan_amount}'


class InstallmentPaid(models.Model):
    """Model to represent payments made towards a loan installment."""
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)  # Foreign key to Loan model
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)  # Foreign key to Employee model
    amount_paid = models.FloatField()  # Amount paid towards the installment
    date_paid = models.DateField(blank=True, null=True)  # Date the installment was paid
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # User who created the record

    def __str__(self):
        return f'{self.amount_paid}'


class Security(models.Model):
    """Model to represent security deposits for employees."""
    
    employee = models.OneToOneField(Employee, on_delete=models.PROTECT)  # One-to-one relationship with Employee
    total_security = models.PositiveIntegerField(default=0, null=True, blank=True)  # Total security amount
    deposited_security = models.PositiveIntegerField(default=0, null=True, blank=True)  # Amount deposited as security
    last_date_submitted = models.DateField(default=timezone.now, blank=True, null=True)  # Last date security was submitted
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # User who created the record

    def __str__(self):
        return f'Deposit for {self.employee.employee_name} - Total Amount: {self.total_security} - Deposited Amount: {self.deposited_security}'


class SecurityDeposits(models.Model):
    """Model to represent individual security deposit transactions."""
    
    security = models.ForeignKey(Security, on_delete=models.CASCADE, blank=True, null=True)  # Link to Security model
    amount = models.PositiveIntegerField(default=0, null=True, blank=True)  # Amount of the deposit
    note = models.CharField(max_length=264, null=True, blank=True)  # Note regarding the deposit
    date_paid = models.DateField(default=timezone.now, blank=True, null=True)  # Date of the deposit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # User who created the record

    def __str__(self):
        return f'{self.security}'


class EOBIPaid(models.Model):
    """Model to represent EOBI deposits for employees."""
    
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, blank=True, null=True)  # Foreign key to Employee
    total_deposit = models.FloatField(default=0.0, blank=True, null=True)  # Total deposit made
    month = models.DateField(default=timezone.now, blank=True, null=True)  # Month of the deposit
    eobi_date_of_joining = models.DateField(blank=True, null=True)  # Date of joining for EOBI
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # User who created the record

    def __str__(self):
        return f'Deposit for {self.employee.employee_name} - Amount: {self.total_deposit}'


class CPFund(models.Model):
    """Model to represent CPF (Contributory Provident Fund) deposits for employees."""
    
    employee = models.OneToOneField(Employee, on_delete=models.PROTECT, null=True, blank=True)  # One-to-one relationship with Employee
    deposited_cp_fund = models.PositiveIntegerField(default=0, null=True, blank=True)  # Amount deposited into CPF
    last_date_submitted = models.DateField(default=timezone.now, blank=True, null=True)  # Last date CPF was submitted
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # User who created the record

    def __str__(self):
        return f'Deposit for {self.employee.employee_name} - Deposited Amount: {self.deposited_cp_fund}'


class CPFundDeposits(models.Model):
    """Model to represent individual CPF deposit transactions."""
    
    cp_fund = models.ForeignKey(CPFund, on_delete=models.CASCADE, blank=True, null=True)  # Link to CPFund model
    amount = models.PositiveIntegerField(default=0, null=True, blank=True)  # Amount of the deposit
    note = models.CharField(max_length=264, null=True, blank=True)  # Note regarding the deposit
    date_paid = models.DateField(default=timezone.now, blank=True, null=True)  # Date of the deposit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # User who created the record

    def __str__(self):
        return f'{self.cp_fund}'


class EmployeeArrears(models.Model):
    """Model to represent any outstanding arrears for employees."""
    
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, blank=True, null=True)  # One-to-one relationship with Employee
    arrears_amount = models.IntegerField(default=0)  # Amount of arrears
    arrears_note = models.CharField(max_length=264, null=True, blank=True)  # Note regarding the arrears

    def __str__(self):
        return f'{self.employee} - {self.arrears_amount}'

