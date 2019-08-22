# CONTAINS ALL THE CUSTOM DIRECTORY USED IN THE PROJECT	

from datetime import datetime
from django.core.exceptions import *
from django.http import HttpResponse
from django.http import Http404  


# EXCEPTION HANDLING METHOD
def error_method(e):
    if isinstance(e,ObjectDoesNotExist):
        print("Record not present: " +str(e))

    elif isinstance(e,MultipleObjectsReturned):
        print("Multiple values present: "+ str(e))
    
    elif isinstance(e,EmptyResultSet):
        print("No matching values present: " +str(e))

    elif isinstance(e,Exception):
        print("Something went wrong: "+ str(e))
        
    else:
        return 200

#AGREEMENT APP
def signature_directory_path(instance,filename):
    print("hey")
    return 'signature/agreement_{0}/{1}/{2}'.format(instance.id, datetime.now().year, filename)


def document_directory_path(filename):
    # file will be uploaded to MEDIA_ROOT/author<id>/<filename>
    # return 'profil/author_{0}/{1}/{2}'.format(instance.id, datetime.now().year, filename)
    return 'document/'

