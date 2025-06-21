# portfolio_analyzer/report_generator.py

"""
This module generates a downloadable PDF report of the portfolio analysis.
It uses Jinja2 to render an HTML template with the analysis data and then
converts the HTML to a PDF using the xhtml2pdf library.
"""
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from io import BytesIO

def generate_pdf_report(username, scores, skills, summary, recommendations):
    """
    Generates a PDF report from the analysis data.

    Args:
        username (str): The GitHub username.
        scores (dict): The dictionary of portfolio scores.
        skills (dict): The dictionary of extracted skills.
        summary (str): The AI-generated summary.
        recommendations (dict): The dictionary of recommendations.

    Returns:
        BytesIO: A byte stream containing the generated PDF file.
                 Returns None if there is an error.
    """
    try:
        # Set up Jinja2 environment to load the template
        env = Environment(loader=FileSystemLoader('portfolio_analyzer/templates/'))
        template = env.get_template('report_template.html')

        # Prepare data for the template
        template_data = {
            "username": username,
            "score": scores.get('total_score', 'N/A'),
            "gpt_feedback": summary,
            "recommendations": recommendations.get('project_ideas', '')
            # You can add more data to the template as needed,
            # such as skill charts or cluster visualizations (as base64 images).
        }
        
        # Render the HTML template with the data
        html_out = template.render(template_data)

        # Create a PDF file in memory
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(
            src=html_out,                # The HTML content
            dest=pdf_buffer              # A file-like object to write to
        )

        # If PDF creation fails, return None
        if pisa_status.err:
            print(f"Error converting HTML to PDF: {pisa_status.err}")
            return None

        # Reset buffer to the beginning
        pdf_buffer.seek(0)
        return pdf_buffer

    except Exception as e:
        print(f"An error occurred during PDF generation: {e}")
        return None

if __name__ == '__main__':
    # --- Example Usage ---
    # This is a dummy example to test the PDF generation logic.
    print("--- Testing PDF Report Generator ---")
    
    # Dummy data
    sample_username = "test_user"
    sample_scores = {'total_score': 85}
    sample_skills = {"Python": 5, "Pandas": 3}
    sample_summary = "This is an excellent portfolio with a strong focus on Python."
    sample_recs = {'project_ideas': 'Consider a project in web development to diversify your skills.'}

    pdf_file = generate_pdf_report(sample_username, sample_scores, sample_skills, sample_summary, sample_recs)

    if pdf_file:
        try:
            with open("portfolio_analysis_report.pdf", "wb") as f:
                f.write(pdf_file.read())
            print("Successfully generated 'portfolio_analysis_report.pdf'.")
        except Exception as e:
            print(f"Error saving PDF file: {e}")
    else:
        print("Failed to generate PDF report.")
    print("------------------------------------") 