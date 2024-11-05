from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from student.models import StudentFeeVoucher, Student, Class
from django.contrib.auth.models import User

class Expense(models.Model):
    """Model representing an expense entry."""
    title = models.CharField(max_length=200)  # Title of the expense
    description = models.TextField(blank=True)  # Description of the expense, optional
    date = models.DateField(auto_now_add=True)  # Date of expense, auto-set on creation
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Expense amount

    def __str__(self):
        return f"{self.title} - {self.amount} on {self.date}"  # String representation of the model

class Bank(models.Model):
    """Model representing bank details."""
    bank_name = models.CharField(max_length=128)  # Name of the bank
    bank_code = models.CharField(max_length=128)  # Code of the bank (e.g., branch code)
    bank_account_no = models.CharField(max_length=128)  # Bank account number
    bank_for_security = models.BooleanField(default=False)  # Flag indicating if bank is used for security purposes
    show_on_voucher = models.BooleanField(default=False)  # Flag indicating if bank should appear on vouchers
    bank_address = models.CharField(max_length=264)  # Bank branch address
    bank_manager = models.CharField(max_length=128, blank=True, null=True)  # Bank manager's name, optional
    bank_contact = models.IntegerField(blank=True, null=True)  # Bank contact number, optional

    def __str__(self):
        return f'{self.bank_code}-{self.bank_name}'  # String representation of the model

class StudentFee(models.Model):
    """Model to record fee payment details for a student."""
    voucher = models.ForeignKey(StudentFeeVoucher, on_delete=models.PROTECT)  # Link to the student's fee voucher
    date_submitted = models.DateField(default=timezone.now)  # Date the fee was submitted
    paid_full = models.BooleanField(default=False)  # Indicates if the fee was paid in full
    paid_full_after_due_date = models.BooleanField(default=False)  # Indicates if full payment was made after due date
    paid_full_after_due_date_without_fine = models.BooleanField(default=False)  # Indicates if payment was made after due date without a fine
    paid_full_after_due_date_waive_fine = models.BooleanField(default=False)  # Indicates if fine was waived for late payment
    amount_paid = models.PositiveIntegerField(blank=True)  # Amount of fee paid
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)  # Bank through which the payment was made
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # User who recorded the fee payment

    def __str__(self):
        return f"Fee of {self.voucher} - {self.amount_paid} on {self.date_submitted}"  # String representation of the model


class SchoolLeavingCertificate(models.Model):
    """Model to represent a student's school leaving certificate details."""
    student = models.ForeignKey(Student, on_delete=models.PROTECT)  # Reference to the student
    admission_date = models.DateField()  # Date when the student was admitted
    admission_class = models.ForeignKey(Class, on_delete=models.PROTECT, related_name='admission_class')  # Class at admission time
    leaving_date = models.DateField(default=timezone.now)  # Date when the student left the school
    last_class = models.ForeignKey(Class, on_delete=models.PROTECT, related_name="last_class")  # Last class attended by the student
    arrears_remaining = models.PositiveIntegerField(default=0)  # Any remaining dues or arrears
    security_refunded = models.PositiveIntegerField()  # Amount of security deposit refunded
    is_refunded = models.BooleanField(default=False)  # Indicates if the security deposit was refunded
    refund_date = models.DateField(null=True, blank=True, default=timezone.now)  # Date of refund (optional)
    paid_to = models.CharField(max_length=64, null=True, blank=True)  # Name of the person to whom refund was paid
    received_by = models.CharField(max_length=128, null=True, blank=True)  # Name of the person who received the certificate
    remarks = models.TextField(null=True, blank=True)  # Additional remarks or notes

    def __str__(self):
        return f"School Leaving Certificate for {self.student}"

class VoucherGenerationRule(models.Model):
    """Model defining rules for voucher generation, including due dates, fines, and extra charges."""
    name = models.CharField(max_length=128, help_text="Example: vouchers for October 2023")  # Rule name for identification
    issue_date = models.DateField()  # Date when vouchers are issued
    due_date = models.DateField()  # Due date for the payment
    late_payment_fine = models.PositiveIntegerField(default=300)  # Fine for late payments
    extra_charges_note = models.CharField(max_length=16, null=True, blank=True)  # Note on additional charges
    extra_charges = models.PositiveIntegerField(default=0)  # Additional charges if any
    active = models.BooleanField(default=False)  # Indicates if the rule is currently active
    apply_arrears = models.BooleanField(default=True)  # Indicates if arrears should be applied
    created = models.DateTimeField(auto_now_add=True)  # Timestamp when the rule was created

    def __str__(self):
        return self.name  # String representation of the model

class SecurityFee(models.Model):
    """Model for recording security fee payments, including refund status."""
    student_fee = models.ForeignKey(
        StudentFee, on_delete=models.CASCADE, null=True, blank=True,
        limit_choices_to={'voucher__is_security_voucher': True}
    )  # Associated fee record, limited to security vouchers only
    student = models.ForeignKey(Student, on_delete=models.PROTECT)  # Reference to the student
    created = models.DateTimeField(auto_now_add=True)  # Timestamp when the security fee was recorded
    date_submitted = models.DateField(default=timezone.now)  # Date the security fee was submitted
    amount_paid = models.PositiveIntegerField()  # Amount of the security fee paid
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)  # Bank through which the payment was made
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # User who recorded the fee

    is_refunded = models.BooleanField(default=False)  # Indicates if the security fee was refunded
    refund_date = models.DateField(null=True, blank=True)  # Date of refund, if applicable
    paid_to = models.CharField(max_length=64, null=True, blank=True)  # Recipient of the refund, if applicable

    def __str__(self):
        return f'{self.student.student_name} | {self.amount_paid}'  # String representation of the model

class MonthClosing(models.Model):
    """Model to record monthly closing information for a bank, including monthly profits."""
    month = models.DateField(default=timezone.now, help_text="Last Day of Month for Closing.")  # Month and year for closing
    profit_by_bank = models.PositiveIntegerField(default=0)  # Profit amount generated by the bank for the month
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)  # Bank associated with this month's closing

    def __str__(self):
        return f'{self.month} | {self.bank} | {self.profit_by_bank}'  # String representation of the model

class OtherDeposits(models.Model):
    """Model for recording other deposits, such as donations or miscellaneous income, into a bank account."""
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, null=True, blank=True)  # Bank where the deposit is made
    date = models.DateField(default=timezone.now)  # Date of the deposit
    remarks = models.CharField(max_length=264, null=True, blank=True)  # Additional notes or remarks about the deposit
    amount = models.PositiveIntegerField(default=0)  # Amount deposited

    def __str__(self):
        return f'{self.bank} | {self.date} | {self.amount}'  # String representation of the model