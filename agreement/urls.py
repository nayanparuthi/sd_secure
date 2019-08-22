from django.urls import path,re_path
from . import views


urlpatterns=[

path('',views.choose_action,name='choose_action'),
path("logout", views.logout_request, name="logout"),
path('master_agreement',views.choose_magreement,name='choose_magreement'),
path('create',views.create_magreement,name='create_magreement'),
path('<int:id>/edit',views.edit_magreement,name='edit_magreement'),
path('<int:id>/delete',views.delete_magreement,name='delete_magreement'),

path('created_agreements',views.created_agreements,name='created_agreements'),
path('created_agreements/create_document',views.create_document,name='create_document'),
path('created_agreements/create_document/fill_details/<int:id>',views.fill_details,name='fill_details'),


path('created_agreements/<int:id>',views.delete_cagreement,name='delete_cagreement'),

path('created_agreements/create_document/edit/<int:id>',views.edit_created_agreement,name='edit_document'),

path('created_agreements/create_document/edit/load_runtime_fields',views.load_runtime_fields,name="load_runtime_fields"),

# path('created_agreements/create_document/send/<int:id>',views.send_email,name='send_email'),
re_path(r'verify/(?P<key>[a-zA-Z0-9]+)',views.send_email,name='send_email'),

# path('created_agreements/create_document/update/<int:id>',views.cagree_update,name='cagree_update'),

path('status/',views.show_cagree,name='show_cagree'),

path('mis_report/',views.mis_report,name='mis_report'),

path('typesearch',views.search_bytype,name='type_search'),

path('datesearch',views.search_bydate,name='date_search'),

path('preview/<int:id>',views.preview_document,name='preview_agreement'),

re_path(r'preview/(?P<key>[a-zA-Z0-9]+)',views.sign_document,name='sign_document'),

path('generatepdf/<int:id>',views.generatepdf,name='generatepdf'),

path('generateotp',views.generate_otp,name='generateotp'),

path('send_sign_email',views.send_sign_email,name='send_sign_email'),

path('terminate/<int:id>',views.terminate,name='terminate'),

path('withdraw/<int:id>',views.withdraw,name='withdraw'),

]