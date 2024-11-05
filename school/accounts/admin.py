from django.contrib import admin
from .models import (
    Expense, Bank, StudentFee, SchoolLeavingCertificate,
    VoucherGenerationRule, SecurityFee, MonthClosing, OtherDeposits
)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'date')
    search_fields = ('title',)
    list_filter = ('date',)


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'bank_code', 'bank_account_no', 'show_on_voucher')
    search_fields = ('bank_name', 'bank_code')
    list_filter = ('bank_for_security', 'show_on_voucher')


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('voucher', 'amount_paid', 'date_submitted', 'paid_full', 'bank')
    search_fields = ('voucher__student__student_name', 'amount_paid')
    list_filter = ('paid_full', 'paid_full_after_due_date', 'bank')


@admin.register(SchoolLeavingCertificate)
class SchoolLeavingCertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'admission_date', 'leaving_date', 'last_class', 'is_refunded')
    search_fields = ('student__student_name', 'received_by')
    list_filter = ('is_refunded', 'refund_date')


@admin.register(VoucherGenerationRule)
class VoucherGenerationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'issue_date', 'due_date', 'late_payment_fine', 'active')
    search_fields = ('name',)
    list_filter = ('active', 'apply_arrears')


@admin.register(SecurityFee)
class SecurityFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount_paid', 'date_submitted', 'is_refunded', 'refund_date')
    search_fields = ('student__student_name', 'amount_paid')
    list_filter = ('is_refunded',)


@admin.register(MonthClosing)
class MonthClosingAdmin(admin.ModelAdmin):
    list_display = ('month', 'bank', 'profit_by_bank')
    list_filter = ('bank',)
    search_fields = ('bank__bank_name',)


@admin.register(OtherDeposits)
class OtherDepositsAdmin(admin.ModelAdmin):
    list_display = ('bank', 'date', 'amount')
    search_fields = ('bank__bank_name', 'remarks')
    list_filter = ('date',)
