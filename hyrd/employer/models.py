from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    about_company = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    educational_requirements = models.TextField(blank=True)
    technical_requirements = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    preferred_qualifications = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    compensation = models.CharField(max_length=100, blank=True)
    document = models.FileField(upload_to='job_documents/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"
