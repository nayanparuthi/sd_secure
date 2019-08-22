from django.contrib import admin
from django.conf.urls import url
from .models import MasterAgreement,CreatedAgreement
from django.utils.html import format_html
from django.urls import reverse
# Register your models here.

# admin.site.site_url = 'http://localhost:8000/'
class MasterAgreementAdmin(admin.ModelAdmin):
	list_display=('name','created_date','updated_date','description','status')
	list_filter=('created_date','status')
	search_fields=('name','description',)
	# list_editable=('status',)

	
class CreatedAgreementAdmin(admin.ModelAdmin):
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

	# def get_urls(self):
	# 	urls = super().get_urls()
	# 	custom_urls =[
 #        url(
 #                r'^preview/$',
 #                self.admin_site.admin_view(self.preview_document),
 #                name='preview_document',
 #            )
 #        ]
	# 	return custom_urls + urls

	# def agreement_actions(self,obj):
	# 	return format_html(
 #            '<a class="button" href="{}">Preview</a>&nbsp;'
 #            '<a class="button" href="{}">Download</a>',
 #            reverse('admin:preview_document')
 #            # reverse('admin:agreement_download', args=[obj.pk]),
 #        )
	# agreement_actions.short_description = 'Actions'
	# agreement_actions.allow_tags = True

	# def preview_document(self):
	# 	created_agreement=CreatedAgreement.objects.all()
	# 	for val in created_agreement:
	# 		if(self.mid==val.id):
	# 			agreementformat=val.document
	# 			status=val.status
	# 			created_agreement_id=val.id
	# 	context={
	# 	'created_agreement_id':created_agreement_id,
	# 	'document':agreementformat,
	# 	'status':status
	# 	}
	# 	return render(request,'agreement/preview_document.html',context)

	list_display=(master_name,'user','creation_date','email','phone','address','signature','status')
	list_filter=('creation_date','status')
	search_fields=('user','mid','email')
	# prepopulated_fields={'mid':(master_name,)}
	ordering = ('creation_date','user')




admin.site.register(MasterAgreement,MasterAgreementAdmin)
admin.site.register(CreatedAgreement,CreatedAgreementAdmin)


