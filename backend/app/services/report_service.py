from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
from typing import Dict, Any

class ReportService:
    def __init__(self, template_dir: str = "app/templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_report(self, student_name: str, data: Dict[str, Any], output_path: str = None) -> bytes:
        """
        Generate a PDF report for a student.
        :param student_name: Name of the student
        :param data: Dictionary of data to inject into template
        :param output_path: If provided, save PDF to this path.
        :return: PDF bytes
        """
        template = self.env.get_template("weekly_report.html")
        
        # Merge context
        context = {
            "student_name": student_name,
            **data
        }
        
        html_content = template.render(context)
        pdf_bytes = HTML(string=html_content).write_pdf()

        if output_path:
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
        
        return pdf_bytes

    def generate_error_worksheet(self, data: Dict[str, Any]) -> bytes:
        """
        오류 찾기 워크시트 PDF 생성
        """
        template = self.env.get_template("error_worksheet.html")
        html_content = template.render(data)
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes

report_service = ReportService()
