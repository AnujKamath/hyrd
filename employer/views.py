from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Company, Job, User,AppliedJob,EmployeeJobRelation
from .forms import CompanyForm, JobForm, LoginForm, RegisterForm
from .utils import extract_text_from_document, extract_job_details
from django.contrib.auth.decorators import login_required
import re
import json
from django.urls import reverse
from django.db.models import Max
from django.urls import reverse, NoReverseMatch


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        print(request)
        print(request.GET)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
                if password == user.password:  
                    request.session['user_id'] = user.id
                    if user.is_employer:
                        return redirect('employer:employer_page', candidate_id=user.candidate_id)
                    else:
                        return redirect('employer:candidate_page', candidate_id=user.candidate_id)

                else:
                    form.add_error(None, "Invalid email or password.")

            except User.DoesNotExist:
                form.add_error(None, "Invalid email or password.")
        return render(request, 'LoginPage.html', {'form': form})
    else:
        form = LoginForm()
        return render(request, 'LoginPage.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("Form is valid") 
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            contact_number = form.cleaned_data['contact_number']
            is_employer = form.cleaned_data['is_employer']

            last_candidate = User.objects.aggregate(Max('candidate_id'))['candidate_id__max']

            if last_candidate:
                new_candidate_id = "CAND" + str(int(last_candidate[4:]) + 1)
            else:
                new_candidate_id = "CAND100"

            User.objects.create(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                contact_number=contact_number,
                is_employer=is_employer,
                candidate_id=new_candidate_id,
            )
            print(f"User created: {email}") #add this
            return redirect('employer:login')
        else:
            print("Form is invalid") #add this
            print(form.errors) #add this
            return render(request, 'LoginPage.html', {'form': form})
    else:
        form = RegisterForm()
    return render(request, 'LoginPage.html', {'form': form})


# @login_required
def candidate_page(request, candidate_id):
    # print(f"candidate_id: {candidate_id}")

    user = get_object_or_404(User, candidate_id=candidate_id)

    if user.is_employer:
        return redirect('employer:employer_page', candidate_id=user.candidate_id)

    if user.id != request.session['user_id']:
        return HttpResponse("Unauthorized", status=401)
    applied_jobs = AppliedJob.objects.filter(candidate=user)
    other_jobs = Job.objects.exclude(appliedjob__candidate=user) 
    return render(request, 'candidate/candidatePage.html', {'applied_jobs': applied_jobs, 'other_jobs': other_jobs, 'user': user})

    # return render(request, 'candidate/candidatePage.html', {'user': user})

def employer_page(request, candidate_id):

    user = get_object_or_404(User, candidate_id=candidate_id)

    if not user.is_employer:
        return redirect('candidate:candidate_page', candidate_id=user.candidate_id)

    if user.id != request.session['user_id']:
        return HttpResponse("Unauthorized", status=401)

    posted_jobs = Job.objects.filter(employeejobrelation__user=user)

    for job in posted_jobs:
        job.applications_count = job.appliedjob_set.count()  # Assuming you still need this

    return render(request, 'employer/employerPage.html', {'posted_jobs': posted_jobs, 'user': user})

def select_candidates(request, candidate_id, job_id):
    """View to display candidates for selection."""
    job = get_object_or_404(Job, id=job_id)
    applications = AppliedJob.objects.filter(job=job)

    try:
        user = get_object_or_404(User, candidate_id=candidate_id)
        print(f"User Candidate ID: {user.candidate_id}")
        print(f"Job ID: {job.id}")

        try:
            url = reverse('select_candidates_confirm', kwargs={'candidate_id': candidate_id, 'job_id': job_id})
            print(f"Resolved URL: {url}")
        except NoReverseMatch as e:
            print(f"URL Resolution Error: {e}")
        
    except User.DoesNotExist:
        print(f"User with candidate_id {candidate_id} not found.")
        return render(request, 'employer/select_candidates.html', {'job': job, 'applications': applications, 'user': None})

    return render(request, 'employer/select_candidates.html', {'job': job, 'applications': applications, 'user': user})

def select_candidates_confirm(request, candidate_id, job_id):
    """View to confirm and update selected candidates' status."""
    if request.method == 'POST':
        selected_candidate_ids = request.POST.getlist('selected_candidates')
        applications = AppliedJob.objects.filter(job_id=job_id, candidate_id__in=selected_candidate_ids)
        applications.update(status='Shortlisted')
        redirect_url = reverse('employer:employer_page', kwargs={'candidate_id': candidate_id})
        return redirect(redirect_url)

    return HttpResponse("Invalid request", status=400)

def create_job(request, candidate_id):
    """Handles the creation of a new job posting."""

    user = get_object_or_404(User, candidate_id=candidate_id)

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = user.employer
            job.save()
            EmployeeJobRelation.objects.create(user=user, job=job)
            return redirect('employer:employer_page', candidate_id=candidate_id)
    else:
        form = JobForm()

    return render(request, 'employer/create_job.html', {'form': form, 'user': user})


def company_list(request):
    companies = Company.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employer:company_list')
    else:
        form = CompanyForm()
    
    return render(request, 'employer/company_list.html', {
        'companies': companies,
        'form': form
    })

def job_list(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    jobs = Job.objects.filter(company=company).order_by('-created_at')
    
    return render(request, 'employer/job_list.html', {
        'company': company,
        'jobs': jobs
    })

def job_create_edit(request, company_id, job_id=None):
    company = get_object_or_404(Company, id=company_id)
    
    if job_id:
        job = get_object_or_404(Job, id=job_id, company=company)
        title = f"Edit Job: {job.title}"
    else:
        job = None
        title = "Create New Job"
    
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            job_instance = form.save(commit=False)
            job_instance.company = company
            job_instance.save()
            return redirect('employer:job_list', company_id=company.id)
        else:
            print("Form errors:", form.errors)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'employer/job_form.html', {
        'form': form,
        'company': company,
        'job': job,
        'title': title
    })

@require_POST
def process_document(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    try:
        if not job.document:
            return JsonResponse({
                'status': 'error',
                'message': 'No document attached to this job'
            }, status=400)
        
        print(f"Processing document for job_id: {job_id}, document: {job.document.path}")
        
        document_text = extract_text_from_document(job.document)
        job_details = extract_job_details(document_text)
        
        # Update job with extracted information
        for field, value in job_details.items():
            if value and hasattr(job, field) and not getattr(job, field):
                setattr(job, field, value)
        
        job.save()
        print(f"Document processed and job updated for job_id: {job_id}")
        
        return JsonResponse({
            'status': 'success',
            'job_details': job_details
        })
    except Exception as e:
        import traceback
        print("Error processing document:")
        print(traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def process_document_extract(request):
    if request.method == 'POST' and request.FILES.get('document'):
        try:
            document = request.FILES['document']
            print(f"Processing uploaded document: {document.name}")
            
            # Extract text and job details
            document_text = extract_text_from_document(document)
            job_details = extract_job_details(document_text)
            
            # Clean up the job details before returning
            cleaned_details = {}
            for key, value in job_details.items():
                if isinstance(value, str):
                    # Remove any runs of spaces
                    cleaned_value = re.sub(r'\s+', ' ', value).strip()
                    cleaned_details[key] = cleaned_value
                else:
                    cleaned_details[key] = value
            
            return JsonResponse({
                'status': 'success',
                'job_details': cleaned_details
            })
        except Exception as e:
            import traceback
            print("Error processing document:")
            print(traceback.format_exc())
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    }, status=400)


# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from .models import Company, Job
# from .forms import CompanyForm, JobForm
# from .utils import extract_text_from_document, extract_job_details

# def company_list(request):
#     companies = Company.objects.all().order_by('name')
    
#     if request.method == 'POST':
#         form = CompanyForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('employer:company_list')
#     else:
#         form = CompanyForm()
    
#     return render(request, 'employer/company_list.html', {
#         'companies': companies,
#         'form': form
#     })

# def job_list(request, company_id):
#     company = get_object_or_404(Company, id=company_id)
#     jobs = Job.objects.filter(company=company).order_by('-created_at')
    
#     return render(request, 'employer/job_list.html', {
#         'company': company,
#         'jobs': jobs
#     })

# # def job_create_edit(request, company_id, job_id=None):
# #     company = get_object_or_404(Company, id=company_id)
    
# #     if job_id:
# #         job = get_object_or_404(Job, id=job_id, company=company)
# #         title = f"Edit Job: {job.title}"
# #     else:
# #         job = None
# #         title = "Create New Job"
    
# #     if request.method == 'POST':
# #         form = JobForm(request.POST, request.FILES, instance=job)
# #         if form.is_valid():
# #             job_instance = form.save(commit=False)
# #             job_instance.company = company
            
# #             if 'document' in request.FILES:
# #                 job_instance.save()
# #                 return JsonResponse({
# #                     'status': 'processing',
# #                     'job_id': job_instance.id
# #                 })
# #             else:
# #                 job_instance.save()
# #                 return redirect('employer:job_list', company_id=company.id)
# #     else:
# #         form = JobForm(instance=job)
    
# #     return render(request, 'employer/job_form.html', {
# #         'form': form,
# #         'company': company,
# #         'job': job,
# #         'title': title
# #     })

# # def job_create_edit(request, company_id, job_id=None):
# #     company = get_object_or_404(Company, id=company_id)
    
# #     if job_id:
# #         job = get_object_or_404(Job, id=job_id, company=company)
# #         title = f"Edit Job: {job.title}"
# #     else:
# #         job = None
# #         title = "Create New Job"
    
# #     if request.method == 'POST':
# #         form = JobForm(request.POST, request.FILES, instance=job)
# #         if form.is_valid():
# #             job_instance = form.save(commit=False)
# #             job_instance.company = company
# #             job_instance.save()
            
# #             # Check if this is an AJAX request with a file upload
# #             if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 'document' in request.FILES:
# #                 return JsonResponse({
# #                     'status': 'processing',
# #                     'job_id': job_instance.id
# #                 })
# #             else:
# #                 return redirect('employer:job_list', company_id=company.id)
# #     else:
# #         form = JobForm(instance=job)
    
# #     return render(request, 'employer/job_form.html', {
# #         'form': form,
# #         'company': company,
# #         'job': job,
# #         'title': title
# #     })

# # def job_create_edit(request, company_id, job_id=None):
# #     company = get_object_or_404(Company, id=company_id)
    
# #     if job_id:
# #         job = get_object_or_404(Job, id=job_id, company=company)
# #         title = f"Edit Job: {job.title}"
# #     else:
# #         job = None
# #         title = "Create New Job"
    
# #     if request.method == 'POST':
# #         form = JobForm(request.POST, request.FILES, instance=job)
# #         if form.is_valid():
# #             job_instance = form.save(commit=False)
# #             job_instance.company = company
# #             job_instance.save()
            
# #             # Check if this is an AJAX request with a file upload
# #             is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
# #             has_document = 'document' in request.FILES
            
# #             if is_ajax and has_document:
# #                 return JsonResponse({
# #                     'status': 'processing',
# #                     'job_id': job_instance.id
# #                 })
# #             else:
# #                 return redirect('employer:job_list', company_id=company.id)
# #     else:
# #         form = JobForm(instance=job)
    
# #     return render(request, 'employer/job_form.html', {
# #         'form': form,
# #         'company': company,
# #         'job': job,
# #         'title': title
# #     })

# def job_create_edit(request, company_id, job_id=None):
#     company = get_object_or_404(Company, id=company_id)
    
#     if job_id:
#         job = get_object_or_404(Job, id=job_id, company=company)
#         title = f"Edit Job: {job.title}"
#     else:
#         job = None
#         title = "Create New Job"
    
#     if request.method == 'POST':
#         # Check if this is just an upload request
#         is_upload_only = request.POST.get('upload_only') == 'true'
        
#         form = JobForm(request.POST, request.FILES, instance=job)
#         if form.is_valid():
#             job_instance = form.save(commit=False)
#             job_instance.company = company
#             job_instance.save()
            
#             if is_upload_only and 'document' in request.FILES:
#                 print("Document uploaded successfully, job_id:", job_instance.id)
#                 return JsonResponse({
#                     'status': 'processing',
#                     'job_id': job_instance.id
#                 })
#             else:
#                 return redirect('employer:job_list', company_id=company.id)
#         else:
#             print("Form errors:", form.errors)
#     else:
#         form = JobForm(instance=job)
    
#     return render(request, 'employer/job_form.html', {
#         'form': form,
#         'company': company,
#         'job': job,
#         'title': title
#     })

# @require_POST
# def process_document(request, job_id):
#     job = get_object_or_404(Job, id=job_id)
    
#     try:
#         if not job.document:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'No document attached to this job'
#             }, status=400)
        
#         print(f"Processing document for job_id: {job_id}, document: {job.document.path}")
        
#         document_text = extract_text_from_document(job.document)
#         job_details = extract_job_details(document_text)
        
#         # Update job with extracted information
#         for field, value in job_details.items():
#             if value and hasattr(job, field) and not getattr(job, field):
#                 setattr(job, field, value)
        
#         job.save()
#         print(f"Document processed and job updated for job_id: {job_id}")
        
#         return JsonResponse({
#             'status': 'success',
#             'job_details': job_details
#         })
#     except Exception as e:
#         import traceback
#         print("Error processing document:")
#         print(traceback.format_exc())
#         return JsonResponse({
#             'status': 'error',
#             'message': str(e)
#         }, status=500)

# # @require_POST
# # def process_document(request, job_id):
# #     job = get_object_or_404(Job, id=job_id)
    
# #     try:
# #         # Make sure the job has a document attached
# #         if not job.document:
# #             return JsonResponse({
# #                 'status': 'error',
# #                 'message': 'No document attached to this job'
# #             }, status=400)
        
# #         document_text = extract_text_from_document(job.document)
# #         job_details = extract_job_details(document_text)
        
# #         # Update job with extracted information
# #         if not job.title and job_details['title']:
# #             job.title = job_details['title']
# #         if not job.about_company and job_details['about_company']:
# #             job.about_company = job_details['about_company']
# #         if not job.summary and job_details['summary']:
# #             job.summary = job_details['summary']
# #         if not job.responsibilities and job_details['responsibilities']:
# #             job.responsibilities = job_details['responsibilities']
# #         if not job.educational_requirements and job_details['educational_requirements']:
# #             job.educational_requirements = job_details['educational_requirements']
# #         if not job.technical_requirements and job_details['technical_requirements']:
# #             job.technical_requirements = job_details['technical_requirements']
# #         if not job.experience_years and job_details['experience_years']:
# #             job.experience_years = job_details['experience_years']
# #         if not job.preferred_qualifications and job_details['preferred_qualifications']:
# #             job.preferred_qualifications = job_details['preferred_qualifications']
# #         if not job.location and job_details['location']:
# #             job.location = job_details['location']
# #         if not job.compensation and job_details['compensation']:
# #             job.compensation = job_details['compensation']
        
# #         job.save()
        
# #         return JsonResponse({
# #             'status': 'success',
# #             'job_details': job_details
# #         })
# #     except Exception as e:
# #         import traceback
# #         print(traceback.format_exc())  # Log detailed error for debugging
# #         return JsonResponse({
# #             'status': 'error',
# #             'message': str(e)
# #         }, status=500)


# # @require_POST
# # def process_document(request, job_id):
# #     job = get_object_or_404(Job, id=job_id)
    
# #     try:
# #         document_text = extract_text_from_document(job.document)
# #         job_details = extract_job_details(document_text)
        
# #         # Update job with extracted information if fields are empty
# #         if not job.title and job_details['title']:
# #             job.title = job_details['title']
# #         if not job.about_company and job_details['about_company']:
# #             job.about_company = job_details['about_company']
# #         if not job.summary and job_details['summary']:
# #             job.summary = job_details['summary']
# #         if not job.responsibilities and job_details['responsibilities']:
# #             job.responsibilities = job_details['responsibilities']
# #         if not job.educational_requirements and job_details['educational_requirements']:
# #             job.educational_requirements = job_details['educational_requirements']
# #         if not job.technical_requirements and job_details['technical_requirements']:
# #             job.technical_requirements = job_details['technical_requirements']
# #         if not job.experience_years and job_details['experience_years']:
# #             job.experience_years = job_details['experience_years']
# #         if not job.preferred_qualifications and job_details['preferred_qualifications']:
# #             job.preferred_qualifications = job_details['preferred_qualifications']
# #         if not job.location and job_details['location']:
# #             job.location = job_details['location']
# #         if not job.compensation and job_details['compensation']:
# #             job.compensation = job_details['compensation']
        
# #         job.save()
        
# #         return JsonResponse({
# #             'status': 'success',
# #             'job_details': job_details
# #         })
# #     except Exception as e:
# #         return JsonResponse({
# #             'status': 'error',
# #             'message': str(e)
# #         }, status=500)

# from django.views.decorators.csrf import csrf_exempt
# import json

# @csrf_exempt
# def process_document_extract(request):
#     if request.method == 'POST' and request.FILES.get('document'):
#         try:
#             document = request.FILES['document']
#             print(f"Processing uploaded document: {document.name}")
            
#             # Extract text and job details
#             document_text = extract_text_from_document(document)
#             job_details = extract_job_details(document_text)
            
#             return JsonResponse({
#                 'status': 'success',
#                 'job_details': job_details
#             })
#         except Exception as e:
#             import traceback
#             print("Error processing document:")
#             print(traceback.format_exc())
#             return JsonResponse({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=500)
    
#     return JsonResponse({
#         'status': 'error',
#         'message': 'Invalid request'
#     }, status=400)
