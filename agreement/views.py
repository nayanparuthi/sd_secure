from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from .models import MasterAgreement,CreatedAgreement
from datetime import datetime
import fileinput
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email import encoders 
from django.core.files import File
from django.template import RequestContext
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
import re
import tkinter
from tkinter import messagebox
from .utils import render_to_pdf 
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from six.moves import urllib
from urllib.request import urlopen
import random, string
from collections import Counter

def choose_action(request):
	return render(request,'agreement/home.html')

@login_required(login_url='/administrator/')
@permission_required("agreement.view_masteragreement",raise_exception=True)
def choose_magreement(request):
	context={
	'master_agreement':MasterAgreement.objects.all()
	}
	return render(request,'agreement/choose_magreement.html',context)

@login_required(login_url='/administrator/')
@permission_required("agreement.add_masteragreement",raise_exception=True)
def create_magreement(request):
	if request.method=='GET':
		return render(request,'agreement/agreement_add.html')
		
	if request.method=='POST':
		name 			  = request.POST.get('name')
		description		  = request.POST.get('description')
		status			  =	request.POST.get('status')
		agreement_content =	request.POST.get('agreement_content')
		
		print("got inside, agreement_content is",agreement_content)
		#extracting all [] data in format
		result=re.findall(r"\['?([A-Za-z0-9\s$&+,:;=?@#|'<>.^*()%!-]+)'?\]",agreement_content)
		print(result)
		# wrong_result=re.findall(r"\['?([A-Za-z0-9\s$&+,:;=?@#|'<>.^*()%!-]+)'?\]",agreement_content)
		edit_fields=""
		#creating a set to avoid duplicates in fields
		normal_set=set([])
		
		for word in result:
			#extracting the first group as we need only the text inside the brackets.
			fields = word
			normal_set.add(fields)

		for item in sorted(normal_set):
			edit_fields = item +"," + edit_fields
		edit_fields= edit_fields[:-1]+""


		if status=='on':
			status=True			
		else:
			status=False

		temp=MasterAgreement.objects.create(name=name,description=description,status=status,created_date=datetime.now,agreement_content=agreement_content,editfields=edit_fields)
		master_agreement=MasterAgreement.objects.get(name=temp)
		context={
		'master_agreement':MasterAgreement.objects.all()
		}
		if(re.search(r"([^A-Za-z0-9\s,]+)",master_agreement.editfields))!=None:
			messages.info(request,"Invalid Field value")
			return redirect('edit_magreement',id=master_agreement.id)
		else:
			messages.info(request,"Master Agreement created successfully")
			return redirect('choose_magreement')

@login_required(login_url='/administrator/')
@permission_required("agreement.change_masteragreement",raise_exception=True)
def edit_magreement(request,id):

	if request.method == "GET":
		agreement=MasterAgreement.objects.get(id=id)
		print("agreement.id is ",agreement.id)
		context={
		'agreement':agreement,
		}
		return render(request,'agreement/magreement_edit.html',context)

	if request.method == "POST":
		agreement=MasterAgreement.objects.get(id=id)
		agreement.name=request.POST.get('name')
		agreement.description=request.POST.get('description')
		agreement.agreement_content=request.POST.get('agreement_content')
		result=re.findall(r"\['?([A-Za-z0-9\s$&+,:;=?@#|'<>.^*()%!-]+)'?\]",request.POST.get('agreement_content'))
		print(result)
		edit_fields=""
		#creating a set to avoid duplicates in fields
		normal_set=set([])
		
		for word in result:
			#extracting the first group as we need only the text inside the brackets.
			fields = word
			normal_set.add(fields)

		# print(sorted(normal_set))
		for item in sorted(normal_set):
			edit_fields = item +"," + edit_fields
		edit_fields= edit_fields[:-1]+""
		print(edit_fields)
		agreement.editfields=edit_fields
		agreement.save()
		context={
		'master_agreement':MasterAgreement.objects.all()
		}
		if(re.search(r"([^A-Za-z0-9\s,]+)",agreement.editfields))!=None:
			print("true")
			messages.info(request,"Invalid Field value")
			return redirect('edit_magreement',id=agreement.id)
		else:
			messages.info(request,"Master Agreement created successfully")
			return redirect('choose_magreement')

@login_required(login_url='/administrator/')
@permission_required("agreement.delete_masteragreement",raise_exception=True)
def delete_magreement(request,id):
	agreement=MasterAgreement.objects.get(id=id)
	agreement.delete()

	messages.info(request,"Master Agreement deleted successfully")
	return redirect('choose_magreement')

@login_required(login_url='/administrator/')
@permission_required("agreement.view_createdagreement",raise_exception=True)
def created_agreements(request):
	masterid=[]
	created_agreement=CreatedAgreement.objects.all()
	for cagree in created_agreement:
		masterid.append(cagree.mid)
	print(masterid)
	master_agreements=MasterAgreement.objects.filter(id__in=masterid)
	agreement_set=[(cagree.creation_date,master.name,cagree.user,cagree.email,cagree.status,cagree.address,cagree.phone,cagree.signature,cagree.id)
	for cagree in created_agreement for master in master_agreements if cagree.mid==master.id]
	paginator = Paginator(agreement_set,5)
	page = request.GET.get('page',1)
	print("page is",page)
	agreement_set_paginate = paginator.get_page(page)
	context={
	'master_agreement':MasterAgreement.objects.all(),
	'agreement_set':agreement_set_paginate,
	}
	return render(request,'agreement/created_agreements.html',context)

@login_required(login_url='/administrator/')
@permission_required("agreement.add_createdagreement",raise_exception=True)
def create_document(request):
	aid=request.POST.get("agreement")
	agreement=MasterAgreement.objects.get(id=aid)
	fields=agreement.editfields
	print(fields)
	edit_fields=fields.split(',')
	print(edit_fields)
	context={
	'agreement':agreement,
	'edit_fields':edit_fields,
	}
	return render(request,'agreement/fill_details.html',context)

@csrf_exempt
@login_required(login_url='/administrator/')
@permission_required('agreement.add_createdagreement',raise_exception=True)
def fill_details(request,id):
	agreement = MasterAgreement.objects.get(id=id)
	agreementformat = agreement.agreement_content
	fields=agreement.editfields
	edit_fields=fields.split(',')
	field_value_pair = ""
	for field in edit_fields:
		if field != "":
			print(field)
			# creating fields that need to be replaced in document
			run_time_field = str('['+field+']')
			# fetching value of field from the form
			fvalue=request.POST.get(field)
			# storing the key value pair of fields and values in database
			field_value_pair = field + ":" + fvalue + "/" + field_value_pair
			# replacing the run time fields with value given in form 
			agreementformat = agreementformat.replace(run_time_field,fvalue)
	
	name = request.POST.get('name')
	address = request.POST.get('address')
	phone = request.POST.get('phone')
	email = request.POST.get('Email')
	signature = request.FILES.get('signature')
	termination_date = request.POST.get('termination_date')
	status = request.POST.get('status')
	is_phone_verify = request.POST.get('is_phone_verfiy')
	if is_phone_verify == 'on':
		phone_verify = True
	else:
		phone_verify = False
	randomnum = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
	temp=CreatedAgreement.objects.create(user=name,address=address,email=email,phone=phone,signature=signature,mid=id,status=status,is_phone_verify=phone_verify,field_value_pair=field_value_pair,termination_date=termination_date,document=agreementformat,key=randomnum)
	temp.save()
	last_agreement=CreatedAgreement.objects.latest('id')
	messages.info(request,"Agreement created successfully for signature")
	id = last_agreement.id
	status=last_agreement.status
	context={
	'created_agreement_id':id,
	'document':agreementformat,
	'status':status
	}
	return render(request,'agreement/home.html',context)

@login_required(login_url='/administrator/')
@permission_required("agreement.delete_createdagreement",raise_exception=True)
def delete_cagreement(request,id):
	cagreement=CreatedAgreement.objects.get(id=id)
	cagreement.delete()
	context={
	'master_agreement':MasterAgreement.objects.all(),
	'created_agreements':CreatedAgreement.objects.all()
	}
	messages.info(request,"Agreement deleted successfully")
	return redirect('created_agreements')

@login_required(login_url='/administrator/')
@permission_required("agreement.change_createdagreement",raise_exception=True)
def edit_created_agreement(request,id):
	if request.method == "GET":
		agreement=CreatedAgreement.objects.get(id=id)
		print(agreement.id)
		print(agreement.mid)
		master=MasterAgreement.objects.get(id=agreement.mid)
		print(master.name)
		edit_fields=[]
		edit_fields_value=[]
		field_value_pair = agreement.field_value_pair.split('/')
		for pair in field_value_pair:
			if pair != "":
				print(pair)
				p = pair.split(':')
				print(p)
				#storing field name in edit_fields
				edit_fields.append(p[0])
				#storing edit field value 
				edit_fields_value.append(p[1])

		edit_fields_pair = zip(edit_fields,edit_fields_value)

		context={
		'cagreement': CreatedAgreement.objects.get(id=id),
		'master_agreement': MasterAgreement.objects.all(),
		'edit_fields_pair': edit_fields_pair,
		'master_name': master.name
		}
		return render(request,'agreement/edit_created_agreement.html',context)

	if request.method == "POST":
		agreement=CreatedAgreement.objects.get(id=id)
		name=request.POST.get('name')
		address=request.POST.get('address')
		phone=request.POST.get('phone')
		email=request.POST.get('Email')
		signature=request.FILES.get('signature')
		mid=request.POST.get("agreement")
		magreement=MasterAgreement.objects.get(id=agreement.mid)
		document=magreement.agreement_content
		edit_fields=magreement.editfields.split(',')
		field_value_pair=""
		for field in edit_fields:
			if field !="":
				run_time_field = str('['+field+']')
				fvalue=request.POST.get(field)
				field_value_pair = field + ":" +fvalue + "/" + field_value_pair
				document=document.replace(run_time_field,fvalue)
		agreement.user=name
		agreement.address=address
		agreement.phone=phone
		agreement.email=email
		agreement.signature=signature
		agreement.mid=mid
		agreement.document=document
		agreement.field_value_pair=field_value_pair
		agreement.save()
		messages.info(request,"Agreement updated successfully")
		context={

			'created_agreement_id':agreement.mid,
			'document':document
		}
		return redirect('created_agreements')

@csrf_exempt
def load_runtime_fields(request):
	
	#sending the edit_fields of the master agreement in json format
	data = request.POST
	data = dict(data.lists())
	for d in data.values():
		print("d is",d)
		print("elements d[i] is:",d[0])
		mid = d[0]
		
	magreement = MasterAgreement.objects.get(id=mid)
	editfields = magreement.editfields.split(',')
	print(editfields)
	
	result = []
	for field in editfields:
		field_names = {}
		if field != "":
			field_names['field'] = field
			result.append(field_names)
	
	fields=json.dumps(result)

	context={
	'agreement':magreement,
	'edit_fields':editfields,
	}
	mimetype= 'application/json'
	return HttpResponse(fields,mimetype)
		
@login_required(login_url='/administrator/')
def send_email(request,key):
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
	return redirect('/status')
		

def send_sign_email(request):
	c_id = request.GET['c_id']
	c_agreement=CreatedAgreement.objects.get(id=c_id)
	m_agreement=MasterAgreement.objects.get(id=c_agreement.mid)
	c_agreement.status="signed"
	c_agreement.save()
	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	msg['Subject'] =  'Songdew has sent you the signed copy of your agreement.'
	msg['From'] = "nayanparuthi@gmail.com"
	msg['To'] = "nainuparuthi@gmail.com"

	#create server
	server = smtplib.SMTP('smtp.gmail.com: 587')
	 
	server.starttls()
	 
	# Login Credentials for sending the mail
	server.login(msg['From'], "Addicted@421")

	# Create the body of the message (an HTML version).
	html = """\
	<html>
	  <head></head>
	  <body>
	    <p>Dear """+c_agreement.user+""",
	    <br>
	    <br>Thank you for approving """+m_agreement.name+"""
	    <br>
	    <br> A copy of the agreement has been attached with the mail.
	    <br>
	    <br>
	    Thanks & Regards,<br>Songdew Media Pvt Ltd
	    </p>
	  </body>
	</html>
	"""
	part1=MIMEText(html,'html')
	msg.attach(part1)
	# open the file to be sent  
	filename = m_agreement.name+"-"+c_agreement.user+str(c_agreement.creation_date)+".pdf"
	try:
		attachment = open("/home/nayan/repo/sd_secure/media/pdf/"+filename, "rb")
	except IOError:
		print("error")
		generatepdf(request,c_id)
		attachment = open("/home/nayan/repo/sd_secure/media/pdf/"+filename, "rb")

	# instance of MIMEBase and named as p 
	p = MIMEBase('application', 'octet-stream')   
	# To change the payload into encoded form 
	p.set_payload((attachment).read()) 
	# encode into base64 
	encoders.encode_base64(p) 
	p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
	# attach the instance 'p' to instance 'msg' 
	msg.attach(p) 
	# send the message via the server.
	server.sendmail(msg['From'], msg['To'], msg.as_string())
	server.quit()
	context={'c_id':c_id,}
	return render(request,'agreement/download_agreement.html',context)

	
@login_required(login_url='/administrator/')
@permission_required("agreement.view_createdagreement",raise_exception=True)
def show_cagree(request):
	sdate=request.GET.get('sdate')
	edate=request.GET.get('edate')
	status=request.GET.get('status')
	agreement_type=request.GET.get('agreement_type')
	print(sdate)
	print(edate)
	master_agreeid=[]
	created_agreelist=CreatedAgreement.objects.all()
	created_doclist={}
	json_list=[]
	for doc in created_agreelist:
		created_doclist={}
		created_doclist["id"]=doc.id
		created_doclist["document"]=doc.document
		created_doclist["key"]=doc.key
		json_list.append(created_doclist)
	js_data = json.dumps(json_list)
	for cagree in created_agreelist:
		master_agreeid.append(cagree.mid)
	print(master_agreeid)
	master_agreelist=MasterAgreement.objects.filter(id__in=master_agreeid)
	print(master_agreelist)
	agreement_set=[(cagree.creation_date, master.name,cagree.user, cagree.email, cagree.status, cagree.id,cagree.key,cagree.document,cagree.is_phone_verify) 
	for cagree in created_agreelist for master in master_agreelist if cagree.mid==master.id]
	paginator = Paginator(agreement_set,8)
	page = request.GET.get('page',1)
	print("page is",page)
	agreement_set_paginate = paginator.get_page(page)
	context={
	'sdate':sdate,
	'edate':edate,
	'status':status,
	'agreement_type':agreement_type,
	'agreement_set':agreement_set_paginate,
	'created_doclist':js_data
	}
	return render(request,'agreement/show_cagree.html',context)

@login_required(login_url='/administrator/')
@permission_required("agreement.view_createdagreement",raise_exception=True)
def search_bytype(request):
	agree=request.POST.get('val')
	print(agree)
	masterid=[]
	masterlist=MasterAgreement.objects.filter(name__iexact=agree)
	for master in masterlist:
		masterid.append(master.id)
	created_agreelist=CreatedAgreement.objects.filter(mid__in=masterid)
	agreement_set=[(cagree.creation_date,master.name,cagree.user,cagree.email,cagree.status,cagree.id)
	for cagree in created_agreelist for master in masterlist if cagree.mid==master.id]
	context={
	'agreement_set':agreement_set
	}
	return render(request,'agreement/show_cagree.html',context)

@login_required(login_url='/administrator/')
@permission_required("agreement.view_createdagreement",raise_exception=True)
def search_bydate(request):
	start_date=request.POST.get('sdate')
	end_date=request.POST.get('edate')
	masterid=[]
	created_agreelist=CreatedAgreement.objects.filter(creation_date__range=(start_date,end_date))
	for cagree in created_agreelist:
		masterid.append(cagree.mid)
	master_agreelist=MasterAgreement.objects.filter(id__in=masterid)
	agreement_set=[(cagree.creation_date,master.name,cagree.user,cagree.email,cagree.status,cagree.id) 
	for cagree in created_agreelist for master in master_agreelist if cagree.mid==master.id ]
	context={
	'agreement_set':agreement_set
	}
	return render(request,'agreement/show_cagree.html',context)

@login_required(login_url='/administrator/')
@permission_required("agreement.view_createdagreement",raise_exception=True)
def preview_document(request,id):
	created_agreement=CreatedAgreement.objects.get(id=id)
	created_agreement_key=created_agreement.key
	agreementformat=created_agreement.document
	status=created_agreement.status
	created_agreement_id=created_agreement.id
	context={
	'created_agreement_id':created_agreement_id,
	'created_agreement_key':created_agreement_key,
	'document':agreementformat,
	'status':status
	}
	return render(request,'agreement/preview_document.html',context)

def sign_document(request,key):
	if(key!=""):
		created_agreement=CreatedAgreement.objects.get(key=key)
		if(created_agreement.status=='signed'):
			message="This agreement has already been signed."
			context={'message':message,}
			return render(request,'agreement/signed_agreement.html',context)
		else:
			created_agreement_id=created_agreement.id
			agreementformat=created_agreement.document
			context={
			'created_agreement_id':created_agreement_id,
			'document':agreementformat,
			}
			return render(request,'agreement/sign_document.html',context)
	else:
		message="This agreement has been terminated."
		context={'message':message,}
		return render(request,'agreement/signed_agreement.html',context)

#View to generate pdf for download link		
def generatepdf(request,id):
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

def generate_otp(request): 
	#Get data from javascript 
	number = request.GET['mobile_no']
	c_id = request.GET['c_id']
	sign = request.GET['sign']
	print(c_id)
	print(number)

	#Generate OTP
	otp = random.randrange(100000,999999,1) 
	message = "Please enter {0} to verify your mobile number on songdew.com".format(otp) # Your message to send. 
	
    # Save the otp and ip address corresponding to user in db 
	created_agreement=CreatedAgreement.objects.get(id=c_id)
	created_agreement.otp = otp 
	created_agreement.receiver_ipaddress = get_client_ip(request)
	created_agreement.save()
    
	# Prepare you post parameter

	values = { 
	'APIKey' : settings.APIKEY, 
	'senderid' : settings.SENDERID,
	'channel' : settings.CHANNEL, 
	'DCS' : settings.DCS,
	'flashsms' : settings.FLASHSMS,
	'text' : message,
	'number' : number,
	'route' : settings.ROUTE 
	} 

	#API URL
	url = "https://www.smsgatewayhub.com/api/mt/SendSMS?"
	# URL encoding the data here. 
	postdata = urllib.parse.urlencode(values)
	print(postdata) 
	url = "{0}{1}".format(url,postdata) 
	print(url) 
	req = urllib.request.Request(url) 
	response = urlopen(req) 
	output = response.read().decode('utf-8')
	print("output type is ",type(json.loads(output))) 
	print("output is ",json.loads(output))
	output = json.loads(output) 

	if output['ErrorMessage'] == 'Success' and output['ErrorCode'] == '000':
		created_agreement.phone=number
		created_agreement.is_phone_verify=True
		agreement_content=get_signatures(request,c_id,sign)
		created_agreement.document=agreement_content
		created_agreement.save()
	context={
	'mobile_no':number,
	'otp':otp,
	'key':created_agreement.key,
	}
	return render(request,'agreement/verify_otp.html',context)

def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR',0)
	return ip

def get_signatures(request,id,sign):
	created_agreement=CreatedAgreement.objects.get(id=id)
	agreement_content=created_agreement.document
	print("before entry",created_agreement.document)
	sign_date=str(datetime.now().date())
	#extracting all {} data in format
	result=re.findall(r"\{'?([A-Za-z0-9\s]+)'?\}",agreement_content)
	edit_fields=""
	field_value_pair=""
	#creating a set to avoid duplicates in fields
	normal_set=set([])
	
	for word in result:
		print(word)
		fields = word
		normal_set.add(fields)

	for item in sorted(normal_set):
		if item != "":
			print(item)
		# creating fields that need to be replaced in document
		run_time_field = str('{'+item+'}')
		print(run_time_field)
		fvalue=""
		if(item=='sign'):
			print(sign)
			fvalue=sign
		if(item=='date'):
			print(sign_date)
			fvalue=	sign_date
		print(fvalue)
		# storing the key value pair of fields and values in database
		field_value_pair = item + ":" + fvalue + "/" + field_value_pair
		# replacing the run time fields with value given in form 
		agreement_content = agreement_content.replace(run_time_field,fvalue)

	created_agreement.document=agreement_content
	created_agreement.save()
	return agreement_content

def mis_report(request):
	master_agreement=MasterAgreement.objects.all()
	created_agreement=CreatedAgreement.objects.all()
	masterid=[]
	m_list=[]
	created_agreement=CreatedAgreement.objects.all()
	for magree in master_agreement:
		m_dict={}
		m_dict['id']=magree.id
		m_dict['name']=magree.name
		m_dict['created_date']=magree.created_date
		m_dict['updated_date']=magree.updated_date
		m_dict['status']=magree.status
		m_dict['count']=0
		m_list.append(m_dict)
	# print(m_list)
	for cagree in created_agreement:
		masterid.append(cagree.mid)
	count_master=dict((x,masterid.count(x)) for x in set(masterid))
	for key1,value in count_master.items():
		print(key1)
		print(value)
		for m in m_list:
			for key2,val in m.items():
				print(val)
				print(key2)
				if(key2=="id"):
					if(val==key1):
						print("match")
						m['count']=value

	# print(m_list)
	context={
	'master_agreement':MasterAgreement.objects.all(),
	'm_list':m_list,
	}
	return render(request,'agreement/mis_report.html',context)

def terminate(request,id):
	created_agreement=CreatedAgreement.objects.get(id=id)
	created_agreement.termination_date=datetime.now().date()
	created_agreement.status="terminated"
	created_agreement.key=""
	created_agreement.save()
	return redirect('/status')

def withdraw(request,id):
	created_agreement=CreatedAgreement.objects.get(id=id)
	created_agreement.status="deactivated"
	created_agreement.save()
	return redirect('/status')

def logout_request(request):
	logout(request)
	messages.info(request, "Logged out successfully!")
	return redirect("main:homepage")