from django import forms
from .models import (Nationality, Country, Province, City, Category, Class, Section,FeeStructure, Student, Admission)

# Reusable mixin for cleaning name fields
class NameCleanMixin:
    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        if len(name) < 3 or not name.isalpha():
            raise forms.ValidationError("Name must be at least 3 characters long and only contain letters.")
        return name

# Base class with dynamic widgets and custom field validation
class BaseModelForm(forms.ModelForm):
    class Meta:
        abstract = True
        fields = '__all__'

    def get_widgets(self, custom_styles):
        """Dynamically assigns widgets with styles based on field types."""
        return {
            field.name: forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': f'Enter {field.verbose_name}',
                'style': f'border: 2px solid {custom_styles.get(field.name, "#6F42C1")}; border-radius: 5px;'
            }) if field.get_internal_type() in ['CharField', 'TextField'] else
            forms.Select(attrs={'class': 'form-select'}) if field.get_internal_type() == 'ForeignKey' else
            forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}) if field.get_internal_type() == 'DateField' else
            None for field in self.Meta.model._meta.fields
        }

    def __init__(self, *args, **kwargs):
        """Apply dynamic widgets on form initialization."""
        super().__init__(*args, **kwargs)
        self.fields.update(self.get_widgets(self.get_field_styles()))

    def get_field_styles(self):
        """Customize field colors for different models."""
        return {
            'name': '#007BFF',
            'country': '#28A745',
            'province': '#FFC107',
            'city': '#FF5733',
            'section': '#17A2B8',
        }

# Forms for specific models
class NationalityForm(NameCleanMixin, BaseModelForm):
    class Meta:
        model = Nationality

class CountryForm(NameCleanMixin, BaseModelForm):
    class Meta:
        model = Country

class ProvinceForm(NameCleanMixin, BaseModelForm):
    class Meta:
        model = Province

class CityForm(NameCleanMixin, BaseModelForm):
    class Meta:
        model = City

class CategoryForm(NameCleanMixin, BaseModelForm):
    class Meta:
        model = Category

class FeeStructureForm(BaseModelForm):
    class Meta:
        model = FeeStructure

class StudentForm(BaseModelForm):
    class Meta:
        model = Student

    def get_field_styles(self):
        return {
            **super().get_field_styles(),
            'gender': '#FF5733',
            'blood_group': '#28A745',
            'profile_picture': '#6F42C1',
        }

class AdmissionForm(BaseModelForm):
    class Meta:
        model = Admission

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('voucher_submitted') and not cleaned_data.get('voucher_details'):
            self.add_error('voucher_details', 'Provide details when the voucher is submitted.')
        return cleaned_data
