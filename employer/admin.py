from django.contrib import admin
from .models import User, Company, Job, EmployeeJobRelation,AppliedJob  # Import your models

admin.site.register(User)
admin.site.register(Company)
admin.site.register(Job)
admin.site.register(EmployeeJobRelation)
admin.site.register(AppliedJob)