from django.db import models

# Create your models here.
from datetime import datetime 
from sd_secure.config import signature_directory_path
from ckeditor.fields import RichTextField
from sd_secure.config import document_directory_path
from django.conf import settings



class MasterAgreement(models.Model):

	CATEGORY_CHOICES=[('tv','TV'),('music','Music')]

	category			= models.CharField(choices=CATEGORY_CHOICES,max_length=255)
	name				= models.CharField(max_length=255)
	created_date		= models.DateField(auto_now_add=True)
	updated_date		= models.DateField(auto_now=True)
	description 		= models.TextField()
	status				= models.BooleanField(default=False)
	agreement_content 	= RichTextField(default=False)
	editfields			= models.CharField(max_length=255,blank=True,null=True)

	class Meta:

		db_table = '{0}_{1}_{2}'.format(settings.DB_TABLE_PREFIX,'agreement','masteragreement')

		permissions = (
				('view_masteragreement', 'Can view songdew master agreement'),
			)

	def __str__(self):
		return self.name


class CreatedAgreement(models.Model):
	mid				   =models.IntegerField()
	user			   =models.CharField(max_length=255)
	email              =models.EmailField(unique=True)
	address			   =models.TextField()
	phone              =models.CharField(max_length=1000,null=True)
	is_phone_verify    =models.BooleanField()
	otp                =models.IntegerField(blank=True, null=True)
	sender_ipaddress   =models.GenericIPAddressField(null=True)
	receiver_ipaddress =models.GenericIPAddressField(null=True)
	creation_date      =models.DateField(auto_now_add=True)
	termination_date   =models.DateField(null=True)
	send_date          =models.DateField(null=True)
	signature          =models.ImageField(upload_to=signature_directory_path,max_length=255,blank=True)
	status             =models.CharField(max_length=255,default='deactivate')
	key                =models.CharField(max_length=255)
	document           =RichTextField()
	field_value_pair   =models.TextField()

	class Meta:

		db_table = '{0}_{1}_{2}'.format(settings.DB_TABLE_PREFIX,'agreement','createdagreement')

		permissions = (
				('view_createdagreement', 'Can view songdew created agreement'),
			)

	def __str__(self):
		return self.user
