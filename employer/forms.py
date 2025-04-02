from django import forms
from .models import Company, Job

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'about_company', 'summary', 'responsibilities',
            'educational_requirements', 'technical_requirements',
            'experience_years', 'preferred_qualifications',
            'location', 'compensation'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'about_company': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'educational_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'technical_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'preferred_qualifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'compensation': forms.TextInput(attrs={'class': 'form-control'}),
        }