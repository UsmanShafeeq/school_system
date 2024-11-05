from django.contrib import admin
from .models import (
    Nationality,
    Religion,
    Province,
    Category,
    Class,
    Section,
    FeeStructure,
    Student,
    Attendance,
    Admission,
)

@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(Religion)
class ReligionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'description')
    search_fields = ('name',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'section_of_class')
    search_fields = ('name',)

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = (
        'category',
        'class_s',
        'child_status',
        'admission_type',
        'total',
    )
    list_filter = ('category', 'class_s', 'child_status', 'admission_type')
    search_fields = ('category__name', 'class_s__name', 'admission_type')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'student_name',
        'roll_no',
        'student_class',
        'student_section',
        'is_verified',
        'date_of_admission',
    )
    list_filter = ('student_class', 'is_verified', 'date_of_admission')
    search_fields = ('student_name', 'roll_no', 'form_b_no')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'is_present')
    list_filter = ('date', 'is_present')
    search_fields = ('student__student_name',)

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'class_required',
        'admission_no',
        'category',
        'date_of_birth',
    )
    list_filter = ('class_required', 'category', 'date_of_birth')
    search_fields = ('full_name', 'admission_no', 'form_b_no')

