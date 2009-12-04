import logging

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse

from models import ViewTracker

def add_view_for(request, content_type_id, object_id):
    ct = ContentType.objects.get(pk=content_type_id)
    myobject = ct.get_object_for_this_type(pk=object_id)
    
    logging.debug('Adding view for %s through web.', myobject)
    
    ViewTracker.add_view_for(myobject)
    
    return HttpResponse()
    