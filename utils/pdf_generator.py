from fpdf import FPDF
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, List

class CareerPlanPDF(FPDF):
    """Custom PDF class for generating career plans"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', uni=True)
        
    def header(self):
        # Logo
        # self.image('logo.png', 10, 8, 33)
        # Arial bold 15
        self.set_font('DejaVu', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'AI Career Counselor - Career Plan', 0, 0, 'C')
        # Line break
        self.ln(20)
        
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # DejaVu italic 8
        self.set_font('DejaVu', '', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        
    def chapter_title(self, title):
        # DejaVu 12
        self.set_font('DejaVu', 'B', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, title, 0, 1, 'L', 1)
        # Line break
        self.ln(4)
        
    def chapter_body(self, body):
        # Times 12
        self.set_font('DejaVu', '', 11)
        # Output justified text
        self.multi_cell(0, 5, body)
        # Line break
        self.ln()
        
    def print_list(self, items):
        # Times 12
        self.set_font('DejaVu', '', 11)
        # List items
        for item in items:
            self.cell(10, 5, '•', 0, 0)
            self.multi_cell(0, 5, item)
            
    def add_roadmap_step(self, step_number, title, description, duration):
        # Step number in a circle
        self.set_font('DejaVu', 'B', 12)
        self.set_fill_color(100, 150, 255)
        self.set_text_color(255, 255, 255)
        self.cell(10, 10, str(step_number), 0, 0, 'C', 1)
        self.set_text_color(0, 0, 0)
        
        # Step title
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, title, 0, 1)
        
        # Duration
        self.set_font('DejaVu', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(10)
        self.cell(0, 5, f"Duration: {duration}", 0, 1)
        self.set_text_color(0, 0, 0)
        
        # Description
        self.set_font('DejaVu', '', 11)
        self.cell(10)
        self.multi_cell(0, 5, description)
        self.ln(5)

def generate_career_plan_pdf(career: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
    """
    Generate a PDF career plan based on career data and user profile.
    
    Args:
        career: Career data dictionary
        user_profile: User profile dictionary
        
    Returns:
        Path to the generated PDF file
    """
    try:
        # Create PDF object
        pdf = CareerPlanPDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # Add current date
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'R')
        
        # Add personalized greeting
        name = user_profile.get('name', 'there')
        pdf.set_font('DejaVu', '', 12)
        pdf.cell(0, 10, f"Hello {name},", 0, 1)
        pdf.multi_cell(0, 5, "Based on your interests and our conversation, I've prepared this personalized career plan for you. This document outlines the key steps and resources to help you pursue a career as a:")
        
        # Career title
        pdf.ln(5)
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 10, career['title'], 0, 1, 'C')
        pdf.ln(5)
        
        # Career overview
        pdf.chapter_title("Career Overview")
        pdf.chapter_body(career['description'])
        
        # Key details
        pdf.chapter_title("Key Details")
        pdf.set_font('DejaVu', '', 11)
        pdf.cell(0, 5, f"Average Salary: ${career['salary']:,}/year", 0, 1)
        pdf.cell(0, 5, f"Growth Rate: {career['growth_rate']*100:.1f}%", 0, 1)
        pdf.cell(0, 5, f"Typical Education: {career['education_level']}", 0, 1)
        pdf.cell(0, 5, f"Field: {career['field_name']}", 0, 1)
        
        # Required skills
        pdf.ln(5)
        pdf.chapter_title("Required Skills")
        pdf.print_list(career['skills'])
        
        # Career roadmap
        pdf.ln(5)
        pdf.chapter_title("Your Career Roadmap")
        pdf.chapter_body("Follow these steps to build your career in this field:")
        pdf.ln(5)
        
        # Add roadmap steps
        for i, step in enumerate(career['roadmap']):
            pdf.add_roadmap_step(i+1, step['title'], step['description'], step['duration'])
        
        # Next steps
        pdf.ln(5)
        pdf.chapter_title("Recommended Next Steps")
        pdf.chapter_body("To get started on your career journey, I recommend the following actions:")
        pdf.ln(3)
        next_steps = [
            "Research educational programs or courses related to this field",
            "Connect with professionals in this industry through LinkedIn or professional organizations",
            "Start building relevant skills through online courses or personal projects",
            "Update your resume to highlight transferable skills and experiences",
            "Set specific, measurable goals for the next 3-6 months"
        ]
        pdf.print_list(next_steps)
        
        # Save PDF to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        pdf.output(temp_file.name)
        
        return temp_file.name
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        # Return a dummy path if there's an error
        return "dummy_career_plan.pdf"