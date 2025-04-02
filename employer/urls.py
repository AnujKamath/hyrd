from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 


app_name = 'employer'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'), 
    # path('logout/', auth_views.LogoutView.as_view(next_page='/employer/login/'), name='logout'),
    path('candidate/<str:candidate_id>/', views.candidate_page, name='candidate_page'),
    path('employer/<str:candidate_id>/', views.employer_page, name='employer_page'),
    path('employer/<str:candidate_id>/select_candidates/<int:job_id>/', views.select_candidates, name='select_candidates'),
    path('employer/<str:candidate_id>/select_candidates_confirm/<int:job_id>/', views.select_candidates_confirm, name='select_candidates_confirm'),
    # path('employer/<str:candidate_id>/p', views.employer_page, name='page'), # Make sure this is present as well.
    path('companies/', views.company_list, name='company_list'),
    path('companies/<int:company_id>/jobs/', views.job_list, name='job_list'),
    path('companies/<int:company_id>/jobs/create/', views.job_create_edit, name='job_create'),
    path('companies/<int:company_id>/jobs/<int:job_id>/edit/', views.job_create_edit, name='job_edit'),
    path('jobs/<int:job_id>/process-document/', views.process_document, name='process_document'),
    path('process-document-extract/', views.process_document_extract, name='process_document_extract'),
]

