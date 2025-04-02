from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Company, Job
from .forms import CompanyForm, JobForm
from .utils import extract_text_from_document, extract_job_details
import re

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
