import os
import spacy
import re
from docx import Document

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    """Clean up extracted text by fixing common PDF extraction issues"""
    # First, normalize newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Fix missing spaces between words (camelCase issues like "SuperAGIispioneeringAI")
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Fix merged words by inserting spaces between lowercase and uppercase sequences
    text = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', text)
    
    # Normalize whitespace within lines
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Remove excessive newlines but preserve paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF with improved handling for structured documents"""
    try:
        # Use PyMuPDF for better extraction
        import fitz
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            text += page_text + "\n"
        
        doc.close()
        
        # Print raw text for debugging
        print(f"Raw extracted text (first 200 chars): {text[:200]}...")
        
        # Apply text cleaning
        cleaned_text = clean_text(text)
        print(f"Cleaned text (first 200 chars): {cleaned_text[:200]}...")
        
        # Process sections for better extraction
        sections = parse_sections(cleaned_text)
        
        # Format the text with clear section markers for better extraction
        structured_text = format_structured_text(cleaned_text, sections)
        
        print(f"Structured text created with {len(sections)} identified sections")
        return structured_text
        
    except Exception as e:
        print(f"Error in PyMuPDF extraction: {str(e)}")
        # Fallback to PyPDF2
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return clean_text(text)

def parse_sections(text):
    """Parse document sections from text"""
    sections = {}
    
    # Look for common section headers
    section_patterns = [
        (r'(?:Job|Position)\s*Title[:\s]+([^\n]+)', 'title'),
        (r'Software\s+Engineer\s+Intern', 'title'),  # Specific title from the example PDF
        (r'Location[:\s]+([^\n]+)', 'location'),
        (r'About\s+(?:the\s+)?Company[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z])', 'about_company'),
        (r'About\s+SuperAGI[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z])', 'about_company'),  # Specific match
        (r'Job\s+(?:Overview|Summary|Description)[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z])', 'summary'),
        (r'Responsibilities[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z])', 'responsibilities'),
        (r'(?:Requirements|Qualifications)[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z])', 'requirements'),
        (r'Technical\s+(?:Requirements|Skills)[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z])', 'technical_requirements'),
        (r'Educational\s+Requirements[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z])', 'educational_requirements'),
        (r'Experience[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z])', 'experience'),
        (r'(?:Preferred|Desired)\s+Qualifications[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z])', 'preferred_qualifications'),
        (r'Compensation|Salary|CTC[:\s]+([^\n]+)', 'compensation'),
    ]
    
    for pattern, section_name in section_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            sections[section_name] = match.group(1).strip()
            print(f"Found section {section_name}: {sections[section_name][:50]}...")
    
    # Look for numbered responsibilities
    if 'responsibilities' not in sections:
        resp_match = re.search(r'Responsibilities[:\s]+(?:\n\s*\d+\.\s+.*)+', text, re.IGNORECASE | re.DOTALL)
        if resp_match:
            sections['responsibilities'] = resp_match.group(0).replace('Responsibilities:', '').strip()
    
    return sections

def format_structured_text(text, sections):
    """Format text with clear section markers for better extraction"""
    structured_text = text
    
    # Add section markers at the beginning
    for section_name, content in sections.items():
        marker = f"\n\n--- {section_name.upper()} ---\n\n"
        structured_text = f"{structured_text}\n{marker}{content}"
    
    return structured_text

def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_document(document):
    print(f"Processing document: {document.name}")
    file_extension = os.path.splitext(document.name)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(document)
    elif file_extension == '.docx':
        return extract_text_from_docx(document)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def extract_job_details(text):
    """Extract job details with improved section recognition"""
    job_details = {
        'title': '',
        'about_company': '',
        'summary': '',
        'responsibilities': '',
        'educational_requirements': '',
        'technical_requirements': '',
        'experience_years': None,
        'preferred_qualifications': '',
        'location': '',
        'compensation': '',
    }
    
    # Extract from structured sections
    section_mappings = {
        'TITLE': 'title',
        'LOCATION': 'location',
        'ABOUT_COMPANY': 'about_company',
        'SUMMARY': 'summary',
        'RESPONSIBILITIES': 'responsibilities',
        'REQUIREMENTS': None,  # Process this specially to split into technical/educational
        'TECHNICAL_REQUIREMENTS': 'technical_requirements',
        'EDUCATIONAL_REQUIREMENTS': 'educational_requirements',
        'EXPERIENCE': None,  # Process this specially to extract years
        'PREFERRED_QUALIFICATIONS': 'preferred_qualifications',
        'COMPENSATION': 'compensation',
    }
    
    for section_name, field_name in section_mappings.items():
        pattern = rf'--- {section_name} ---\s*\n\s*(.*?)(?=\n\s*---|$)'
        match = re.search(pattern, text, re.DOTALL)
        if match and field_name:
            job_details[field_name] = match.group(1).strip()
    
    # If we couldn't find a title in the sections, look for it directly
    if not job_details['title']:
        # Try to find Software Engineer Intern or similar titles
        title_match = re.search(r'Software\s+Engineer\s+Intern', text, re.IGNORECASE)
        if title_match:
            job_details['title'] = title_match.group(0).strip()
    
    # If we don't have location yet, look for it directly
    if not job_details['location']:
        location_match = re.search(r'Location[:\s]+([^\n]+)', text, re.IGNORECASE)
        if location_match:
            job_details['location'] = location_match.group(1).strip()
    
    # Extract About the Company if we don't have it
    if not job_details['about_company']:
        about_match = re.search(r'About\s+(?:the\s+)?Company[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z])', text, re.IGNORECASE | re.DOTALL)
        if about_match:
            job_details['about_company'] = about_match.group(1).strip()
            
        # Try specific pattern for the example PDF
        about_match = re.search(r'About\s+SuperAGI[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z]|\s*Job\s+Overview)', text, re.IGNORECASE | re.DOTALL)
        if about_match and not job_details['about_company']:
            job_details['about_company'] = about_match.group(1).strip()
    
    # Extract Job Summary if missing
    if not job_details['summary']:
        summary_match = re.search(r'Job\s+(?:Overview|Summary|Description)[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z]|\s*Responsibilities)', text, re.IGNORECASE | re.DOTALL)
        if summary_match:
            job_details['summary'] = summary_match.group(1).strip()
    
    # Extract or split technical requirements
    if not job_details['technical_requirements']:
        # First look for obvious technical requirements sections
        tech_match = re.search(r'Technical\s+(?:Requirements|Skills)[:\s]+(.*?)(?=\n\s*\n|\n\s*[A-Z])', text, re.IGNORECASE | re.DOTALL)
        if tech_match:
            job_details['technical_requirements'] = tech_match.group(1).strip()
        # If not found, try to extract from responsibilities
        elif job_details['responsibilities']:
            tech_skills = []
            resp_lines = job_details['responsibilities'].split('\n')
            
            for line in resp_lines:
                if re.search(r'software|develop|code|program|technical|algorithm|debug|test', line, re.IGNORECASE):
                    tech_skills.append(line.strip())
            
            if tech_skills:
                job_details['technical_requirements'] = '\n'.join(tech_skills)
    
    # Try to extract experience years from the text
    if not job_details['experience_years']:
        exp_match = re.search(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', text, re.IGNORECASE)
        if exp_match:
            try:
                job_details['experience_years'] = int(exp_match.group(1))
            except ValueError:
                pass
    
    # Remove redundant information
    # If about_company contains the location info, clean it up
    if job_details['location'] and job_details['about_company'].startswith(job_details['location']):
        job_details['about_company'] = job_details['about_company'][len(job_details['location']):].strip()
    
    # Print what was found for debugging
    for key, value in job_details.items():
        if value:
            print(f"Final {key}: {value[:50]}...")
    
    return job_details