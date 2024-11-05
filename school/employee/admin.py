from django.contrib import admin
from .models import (
    StaffPerformance,
    IncrementOrder,
    Increment,
    Loan,
    InstallmentPaid,
    Security,
    SecurityDeposits,
    EOBIPaid,
    CPFund,
    CPFundDeposits,
    EmployeeArrears,
)

# Inline model for InstallmentPaid to easily manage loan installment payments
class InstallmentPaidInline(admin.TabularInline):
    model = InstallmentPaid
    extra = 1  # Number of empty forms to display
    fields = ('amount_paid', 'date_paid', 'created_by')
    readonly_fields = ('created_by',)  # Make created_by read-only

@admin.register(StaffPerformance)
class StaffPerformanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date_evaluated', 'rating')
    list_filter = ('rating', 'date_evaluated')
    search_fields = ('employee__employee_name',)
    date_hierarchy = 'date_evaluated'

@admin.register(IncrementOrder)
class IncrementOrderAdmin(admin.ModelAdmin):
    list_display = ('note', 'percentage_increment', 'created')
    search_fields = ('note',)

@admin.register(Increment)
class IncrementAdmin(admin.ModelAdmin):
    list_display = ('order', 'pay_structure', 'amount', 'created')
    list_filter = ('order',)
    search_fields = ('order__note',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('employee', 'loan_amount', 'remaining_amount', 'installments_paid')
    search_fields = ('employee__employee_name',)
    list_filter = ('employee',)

    inlines = [InstallmentPaidInline]  # Allow inline management of installment payments

@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    list_display = ('employee', 'total_security', 'deposited_security', 'last_date_submitted')
    search_fields = ('employee__employee_name',)

@admin.register(SecurityDeposits)
class SecurityDepositsAdmin(admin.ModelAdmin):
    list_display = ('security', 'amount', 'note', 'date_paid')
    search_fields = ('security__employee__employee_name',)
    list_filter = ('date_paid',)

@admin.register(EOBIPaid)
class EOBIPaidAdmin(admin.ModelAdmin):
    list_display = ('employee', 'total_deposit', 'month')
    search_fields = ('employee__employee_name',)

@admin.register(CPFund)
class CPFundAdmin(admin.ModelAdmin):
    list_display = ('employee', 'deposited_cp_fund', 'last_date_submitted')
    search_fields = ('employee__employee_name',)

@admin.register(CPFundDeposits)
class CPFundDepositsAdmin(admin.ModelAdmin):
    list_display = ('cp_fund', 'amount', 'note', 'date_paid')
    search_fields = ('cp_fund__employee__employee_name',)
    list_filter = ('date_paid',)

@admin.register(EmployeeArrears)
class EmployeeArrearsAdmin(admin.ModelAdmin):
    list_display = ('employee', 'arrears_amount', 'arrears_note')
    search_fields = ('employee__employee_name',)

