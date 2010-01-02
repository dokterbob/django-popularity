# This file is part of django-popularity.
# 
# django-popularity: A generic view- and popularity tracking pluggable for Django. 
# Copyright (C) 2008-2009 Mathijs de Bruin
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
    