from django.contrib import admin
from .models import Nationality, Country, Province, City, Category, Class, Section, FeeStructure, Student, Admission

# 1. Nationality Admin
@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# 2. Country Admin
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# 3. Province Admin
@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ('name',)

# 4. City Admin
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'province')
    list_filter = ('province',)
    search_fields = ('name',)

# 5. Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# 6. Class Admin
@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

# 7. Section Admin
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'related_class')
    list_filter = ('related_class',)
    search_fields = ('name',)

# 8. FeeStructure Admin
@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('admission_type', 'related_class', 'total')
    list_filter = ('admission_type', 'related_class')
    search_fields = ('related_class__name',)
    readonly_fields = ('total',)  # Making total read-only to prevent manual edits

# 9. Student Admin
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'gender', 'contact_number')
    list_filter = ('gender', 'nationality', 'religion')
    search_fields = ('first_name', 'last_name', 'contact_number', 'father_name')
    readonly_fields = ('profile_picture',)  # Display image field as read-only if applicable

# 10. Admission Admin
@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('roll_no','student', 'admission_date', 'class_assigned', 'section', 'admission_confirmed', 'total_fee', 'voucher_submitted', 'voucher_submission_date', 'fee_status')
    list_filter = ('student_status', 'admission_type', 'class_assigned', 'section')
    search_fields = ('student__first_name', 'student__last_name', 'roll_no')
    readonly_fields = ('total_fee', 'confirmation_date', 'voucher_submission_date')
    actions = ['confirm_admission']

    def confirm_admission(self, request, queryset):
        """Custom admin action to confirm multiple admissions at once."""
        queryset.update(admission_confirmed=True)
    confirm_admission.short_description = "Confirm selected admissions"

