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

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class RegisterForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    contact_number = forms.CharField(required=False)
    is_employer = forms.BooleanField(required=False)