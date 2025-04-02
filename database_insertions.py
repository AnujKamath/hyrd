from django.contrib.auth.models import User
from employer.models import Employer, Job
from candidate.models import Candidate, AppliedJob

def populate_database():
    """
    Populates the database with sample data.
    """

    # Create Employers
    employer1 = Employer.objects.create(name="Global Solutions Ltd.", about_company="We provide innovative solutions.")
    employer2 = Employer.objects.create(name="Tech Innovators Inc.", about_company="Leading tech company.")

    # Create Users (Employers)
    user_employer1 = User.objects.create_user(username="global_solutions", password="password123", email="global@example.com", is_employer=True)
    user_employer1.employer = employer1
    user_employer1.save()

    user_employer2 = User.objects.create_user(username="tech_innovators", password="password456", email="tech@example.com", is_employer=True)
    user_employer2.employer = employer2
    user_employer2.save()

    # Create Candidates
    candidate1 = Candidate.objects.create(first_name="Alice", last_name="Smith", email="alice@example.com")
    candidate2 = Candidate.objects.create(first_name="Bob", last_name="Johnson", email="bob@example.com")
    candidate3 = Candidate.objects.create(first_name="Charlie", last_name="Williams", email="charlie@example.com")

    # Create Users (Candidates)
    user_candidate1 = User.objects.create_user(username="alice", password="password789", email="alice@example.com", candidate=candidate1)
    user_candidate1.save()

    user_candidate2 = User.objects.create_user(username="bob", password="password101", email="bob@example.com", candidate=candidate2)
    user_candidate2.save()

    user_candidate3 = User.objects.create_user(username="charlie", password="password112", email="charlie@example.com", candidate=candidate3)
    user_candidate3.save()


    # Create Jobs
    job1 = Job.objects.create(
        title="Data Analyst",
        company=employer1,
        summary="Analyze data and provide insights.",
        responsibilities="Data analysis, reporting.",
        educational_requirements="Bachelor's degree in Statistics.",
        technical_requirements="Python, SQL.",
        experience_years=2,
        location="New York",
        compensation="80000"
    )

    job2 = Job.objects.create(
        title="Software Engineer",
        company=employer2,
        summary="Develop software applications.",
        responsibilities="Coding, testing, debugging.",
        educational_requirements="Bachelor's degree in Computer Science.",
        technical_requirements="Java, JavaScript.",
        experience_years=3,
        location="San Francisco",
        compensation="100000"
    )

    job3 = Job.objects.create(
        title="Marketing Specialist",
        company=employer1,
        summary="Drive marketing campaigns.",
        responsibilities="Social media, content creation.",
        educational_requirements="Bachelor's degree in Marketing.",
        technical_requirements="Google Analytics, SEO.",
        experience_years=1,
        location="London",
        compensation="60000"
    )

    # Create Applied Jobs
    AppliedJob.objects.create(candidate=candidate1, job=job1, status="Applied")
    AppliedJob.objects.create(candidate=candidate2, job=job2, status="Interviewing")
    AppliedJob.objects.create(candidate=candidate1, job=job3, status="Applied")
    AppliedJob.objects.create(candidate=candidate3, job=job1, status="Applied")

if __name__ == "__main__":
    # Ensure Django environment is set up
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings") #replace your_project_name
    import django
    django.setup()

    populate_database()
    print("Database populated successfully.")