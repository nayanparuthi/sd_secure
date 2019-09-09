from django.contrib import admin
from django.conf.urls import url
from django import forms
from django.forms import ModelForm
from .models import MasterAgreement,CreatedAgreement
from django.utils.html import format_html
from .utils import render_to_pdf 
from django.urls import reverse,path,re_path
from django.utils.safestring import mark_safe
from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponseRedirect,HttpResponse
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email import encoders 
from .views import get_client_ip
# Register your models here.

class MasterAgreementAdminForm(forms.ModelForm):
	
	class Meta:
		model = MasterAgreement

		CATEGORY_CHOICES=[('tv','TV'),('music','Music')]

		fields=['category','name','status','agreement_content']
		widgets = {
            'category':forms.Select(choices=CATEGORY_CHOICES,attrs={'class': 'inline'}),
        }

class MasterAgreementAdmin(admin.ModelAdmin):
	class Media:
		js=('toggle.js',)
		css={'all': ('admin/css/admin.css',),}
	list_display=('category','name','created_date','updated_date','description','is_Status')
	list_filter=('created_date','status')
	search_fields=('name','description',)
		

	def get_urls(self):
		urls = super(MasterAgreementAdmin, self).get_urls()
		urlpatterns=[
		path('toggle_status', self.admin_site.admin_view(self.toggle_status), name="toggle_status"),
        ]
		return urlpatterns + urls

	def is_Status(self, obj):
		if(obj.status):
			return mark_safe('<div type="button" name="status" class="status green" value="1" ><img class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"> <img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
		elif(not obj.status):
			return mark_safe('<div type="button" name="status" class="status red" value="0" ><img  class="iconYes" style="width:20px; height:20px" src="/static/admin/img/icon-yes.svg"><img class="iconNo" style="width:20px; height:20px" src="/static/admin/img/icon-no.svg"></div>')
	is_Status.boolean = False
	is_Status.admin_order_field = 'status'
	is_Status.short_description  = 'Status'

	def toggle_status(self,request):
		m_id=request.GET['id']
		print(m_id)
		status=request.GET['status']
		print(status)
		m_agreement=MasterAgreement.objects.get(id=m_id)
		if(status=='1'):
			m_agreement.status='0'
			m_agreement.save()
			data={
			'status':"0",
			}
			return HttpResponse(json.dumps(data))

		else:
			m_agreement.status='1'
			m_agreement.save()
			data={
			'status':"0",
			}
			return HttpResponse(json.dumps(data))
	
class CreatedAgreementAdmin(admin.ModelAdmin):

	class Media:
		js=('preview.js',)

	change_list_template = "agreement/change_list.html"

	def get_urls(self):
		urls = super(CreatedAgreementAdmin, self).get_urls()
		urlpatterns=[
		 url(r'generatepdf/$', self.admin_site.admin_view(self.generatepdf), name="generatepdf"),
		 url(r'terminate/$', self.admin_site.admin_view(self.terminate), name="terminate"),
		 url(r'withdraw/$', self.admin_site.admin_view(self.withdraw), name="withdraw"),
		 re_path(r'email/verify/(?P<key>[a-zA-Z0-9]+)',self.admin_site.admin_view(self.send_email),name='send_email'),
        ]
		return urlpatterns + urls


	def master_category(self):
		ma_list = MasterAgreement.objects.all()
		for val in ma_list :
			if (self.mid == val.id):
				return val.category

	def master_name(self):
		ma_list = MasterAgreement.objects.all()
		for val in ma_list :
			if (self.mid == val.id):
				return val.name

	def master_actions(self):
		ca_list = CreatedAgreement.objects.all()
		for val in ca_list :
			if (self.mid == val.id):
				ca_list.delete()

	def agreement_actions(self,obj):
		if obj.status == "signed":
			return format_html(
				'<a class="button terminate" href="terminate?id={0}" id="{0}" style="background:red; display:none">Terminate</a>&nbsp;'
				'<a class="button withdraw" href="withdraw?id={1}" id="{1}" style="display:none">Withdraw</a>&nbsp;'
	            '<a class="button preview" id="{2}" data-toggle="modal" data-target="#myModal" data-id="{3}" style="color:white">Preview</a>&nbsp;'
	            '<a class="button download" href="generatepdf?id={4}" id="{5}">Download</a>'
	            ,obj.id,obj.id,obj.key,obj.document,obj.id,obj.id
	        )
		else:
			return format_html(
				'<a class="button terminate" href="terminate?id={0}" id="{0}" style="background:red">Terminate</a>&nbsp;'
				'<a class="button withdraw" href="withdraw?id={1}" id="{1}">Withdraw</a>&nbsp;'
	            '<a class="button preview" id="{2}" data-toggle="modal" data-target="#myModal" data-id="{3}" style="color:white">Preview</a>&nbsp;'
	            '<a class="button download"  href="generatepdf?id={4}" id="{5}">Download</a>'
	            ,obj.id,obj.id,obj.key,obj.document,obj.id,obj.id
	        )
	agreement_actions.short_description = 'Actions'
	agreement_actions.allow_tags = True

	
	def terminate(self,request):
		id=request.GET.get('id')
		created_agreement=CreatedAgreement.objects.get(id=id)
		created_agreement.termination_date=datetime.now().date()
		created_agreement.status="terminated"
		created_agreement.key=""
		created_agreement.save()
		return HttpResponseRedirect("/admin/agreement/createdagreement/")

	def withdraw(self,request):
		id=request.GET.get('id')
		created_agreement=CreatedAgreement.objects.get(id=id)
		created_agreement.status="deactivated"
		created_agreement.save()
		return HttpResponseRedirect("/admin/agreement/createdagreement/")


	def generatepdf(self,request):
		id=request.GET.get('id')
		created_agreement=CreatedAgreement.objects.get(id=id)
		master_agreement=MasterAgreement.objects.get(id=created_agreement.mid)
		agreementformat=created_agreement.document
		filename = master_agreement.name+"-"+created_agreement.user+str(created_agreement.creation_date)+".pdf"
		context={
	    'document':agreementformat,
	    'filename':filename,
	    }
		pdf=render_to_pdf('agreement/generatepdf.html',context)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			content = "inline; filename='%s'" %(filename)
			download = request.GET.get("download")
			if download:
				content = "attachment; filename='%s'" %(filename)
				response['Content-Disposition'] = content
			return response
		return HttpResponse("Not found")

	def send_email(self,request,key):
		senddate=datetime.now().date()
		c_agreement=CreatedAgreement.objects.get(key=key)
		m_agreement=MasterAgreement.objects.get(id=c_agreement.mid)
		c_agreement.status="sent"
		c_agreement.send_date=senddate
		c_agreement.sender_ipaddress=get_client_ip(request)
		c_agreement.save()
		
		# Create message container - the correct MIME type is multipart/alternative.
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "Songdew has sent you "+m_agreement.name+"-"+c_agreement.user+" to approve."
		msg['From'] = "nayanparuthi@gmail.com"
		msg['To'] = "nainuparuthi@gmail.com"

		#create server
		server = smtplib.SMTP('smtp.gmail.com: 587')
		 
		server.starttls()
		 
		# Login Credentials for sending the mail
		server.login(msg['From'], "Addicted@421")

		# Create the body of the message (HTML version).
		html = """\
		<html>
		  <head></head>
		  <body>
		    <p>Dear """+c_agreement.user+""",
		    <br>
		    <br>Please sign and approve the agreement.
		    <br>
		    <br>This agreement expires after completion of 10 days from the date of receipt of the agreement.
		     Further, any physical signature or stamp on this document shall not be considered as a valid agreement.
		    <br><br>
		    <a href="http://127.0.0.1:8000/preview/"""+c_agreement.key+"""">
		    Click here to review and approve """+m_agreement.name+"""-"""+c_agreement.user+"""</a><br><br>
		    After you approve the agreement, all parties will receive a final PDF copy by email.
		    <br>
		    <br>
		    Thanks & Regards,<br>Songdew Media Pvt Ltd
		    </p>
		  </body>
		</html>
		"""
		part1=MIMEText(html,'html')
		msg.attach(part1)
		# send the message via the server.
		server.sendmail(msg['From'], msg['To'], msg.as_string())
		 
		server.quit()
		return HttpResponseRedirect("/admin/agreement/createdagreement/")

	list_display=(master_category,master_name,'user','creation_date','email','phone','address','status','agreement_actions')
	list_filter=('creation_date','status')
	search_fields=('user','mid','email')
	ordering = ('creation_date','user')




admin.site.register(MasterAgreement,MasterAgreementAdmin)
admin.site.register(CreatedAgreement,CreatedAgreementAdmin)


