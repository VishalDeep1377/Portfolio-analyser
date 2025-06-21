# portfolio_analyzer/linkedin_parser.py

"""
This module (optional) parses a user's LinkedIn profile from an HTML file
export. It uses BeautifulSoup to extract key sections like summary, experience,
skills, and certifications.
"""
from bs4 import BeautifulSoup
import re
import json
import pdfplumber

def parse_linkedin_pdf(pdf_file):
    """
    Parses a LinkedIn profile from a PDF file.
    
    Args:
        pdf_file: A file-like object for the PDF.

    Returns:
        dict: A dictionary containing parsed data.
    """
    full_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    
    parsed_data = {
        "summary": "",
        "experience": [],
        "skills": [],
        "certifications": [],
        "education": []
    }

    # Use regex to find sections. Case-insensitive and multiline.
    # Summary
    summary_match = re.search(r"Summary\n(.*?)\nExperience", full_text, re.DOTALL | re.IGNORECASE)
    if summary_match:
        parsed_data["summary"] = summary_match.group(1).strip()
        
    # Experience
    experience_match = re.search(r"Experience\n(.*?)\nEducation", full_text, re.DOTALL | re.IGNORECASE)
    if experience_match:
        # Split by potential job titles (assuming they are on their own line)
        jobs = experience_match.group(1).strip().split('\n\n')
        for job in jobs:
            lines = job.split('\n')
            if len(lines) >= 2:
                parsed_data["experience"].append({
                    "title": lines[0],
                    "company": lines[1]
                })

    # Education
    education_match = re.search(r"Education\n(.*?)\nLicenses & certifications", full_text, re.DOTALL | re.IGNORECASE)
    if education_match:
        # Simple split, assumes "University Name" on one line and "Degree" on the next.
        schools = education_match.group(1).strip().split('\n\n')
        for school in schools:
            lines = school.split('\n')
            if len(lines) >= 2:
                parsed_data["education"].append({
                    "school": lines[0],
                    "degree": lines[1]
                })

    # Licenses & Certifications
    certs_match = re.search(r"Licenses & certifications\n(.*?)\nSkills", full_text, re.DOTALL | re.IGNORECASE)
    if certs_match:
        certs = certs_match.group(1).strip().split('\n\n')
        for cert in certs:
            lines = cert.split('\n')
            if len(lines) >= 2:
                parsed_data["certifications"].append({
                    "title": lines[0],
                    "issuer": lines[1]
                })

    # Skills
    skills_match = re.search(r"Skills & endorsements\n(.*?)\n", full_text, re.DOTALL | re.IGNORECASE)
    if skills_match:
        # This section is often messy. We'll just grab lines of text.
        skills_text = skills_match.group(1).strip()
        # Simple split, might need refinement based on actual PDF structure
        parsed_data["skills"] = [skill.strip() for skill in skills_text.split('\n') if len(skill.strip()) > 1]

    return parsed_data

def parse_linkedin_profile(html_content):
    """
    Parses the HTML content of a LinkedIn profile export.

    Note: This parser is based on the general structure of LinkedIn profile exports.
    LinkedIn may change its HTML structure, which could break this parser.

    Args:
        html_content (str): The HTML content of the LinkedIn profile page.

    Returns:
        dict: A dictionary containing the parsed 'summary', 'experience', 'skills',
              and 'certifications'.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    parsed_data = {
        "summary": "",
        "experience": [],
        "skills": [],
        "certifications": [],
        "education": []
    }

    # --- Extract Summary (About section) ---
    # LinkedIn often uses a section with an id like 'about' or a class for the summary.
    # A common pattern is a div containing the text "About". We find the sibling content.
    about_section = soup.find('section', class_=re.compile(r'about'))
    if about_section:
        # Look for a span or div that contains the actual text.
        summary_div = about_section.find('div', class_=re.compile(r'full-profile')) # This class can vary
        if summary_div:
            parsed_data["summary"] = summary_div.get_text(separator="\n", strip=True)

    # --- Extract Experience ---
    experience_section = soup.find('section', class_=re.compile(r'experience'))
    if experience_section:
        # Find all list items, as each job is often in an <li>
        jobs = experience_section.find_all('li', class_=re.compile(r'item'))
        for job in jobs:
            title_tag = job.find('h3', class_=re.compile(r'title'))
            company_tag = job.find('p', class_=re.compile(r'subtitle'))
            description_tag = job.find('div', class_=re.compile(r'description'))
            
            if title_tag and company_tag:
                parsed_data["experience"].append({
                    "title": title_tag.get_text(strip=True),
                    "company": company_tag.get_text(strip=True),
                    "description": description_tag.get_text(separator="\\n", strip=True) if description_tag else ""
                })

    # --- Extract Education ---
    education_section = soup.find('section', class_=re.compile(r'education'))
    if education_section:
        schools = education_section.find_all('li', class_=re.compile(r'item'))
        for school in schools:
            school_tag = school.find('h3', class_=re.compile(r'title'))
            degree_tag = school.find('p', class_=re.compile(r'subtitle'))
            if school_tag and degree_tag:
                parsed_data["education"].append({
                    "school": school_tag.get_text(strip=True),
                    "degree": degree_tag.get_text(strip=True)
                })

    # --- Extract Skills ---
    skills_section = soup.find('section', class_=re.compile(r'skills'))
    if skills_section:
        # Skills are often in a list of <li> tags as well
        skill_tags = skills_section.find_all('li', class_=re.compile(r'skill'))
        for skill_tag in skill_tags:
            # Find the primary text for the skill
            name_tag = skill_tag.find('span', class_=re.compile(r'skill-name'))
            if name_tag:
                parsed_data["skills"].append(name_tag.get_text(strip=True))

    # --- Extract Certifications ---
    certs_section = soup.find('section', class_=re.compile(r'certifications'))
    if certs_section:
        cert_tags = certs_section.find_all('li', class_=re.compile(r'item'))
        for cert_tag in cert_tags:
            title_tag = cert_tag.find('h3', class_=re.compile(r'title'))
            issuer_tag = cert_tag.find('p', class_=re.compile(r'subtitle'))
            if title_tag:
                parsed_data["certifications"].append({
                    "title": title_tag.get_text(strip=True),
                    "issuer": issuer_tag.get_text(strip=True) if issuer_tag else "N/A"
                })

    return parsed_data 