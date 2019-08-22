from io import BytesIO #A stream implementation using an in-memory bytes buffer
                       # It inherits BufferIOBase
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
 
#pisa is a html2pdf converter using the ReportLab Toolkit,
#the HTML5lib and pyPdf.
import xhtml2pdf
from xhtml2pdf import pisa  

#define render_to_pdf() function
 
def render_to_pdf(template_src, context):
	print(context)
	template = get_template(template_src)
	html  = template.render(context)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
	destination = settings.PDF_ROOT
	file = open(destination + context['filename'], "w+b")
	pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file, encoding='utf-8')
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None