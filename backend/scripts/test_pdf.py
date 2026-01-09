from weasyprint import HTML
import sys

try:
    print("Generating PDF...", file=sys.stderr)
    HTML(string='<h1>Hello, world!</h1>').write_pdf('test.pdf')
    print("PDF Generated successfully.", file=sys.stderr)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
