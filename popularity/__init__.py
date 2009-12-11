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
from django.db.models.signals import post_save, pre_delete

from models import ViewTracker

VERSION = (0, 1, None)

def post_save_handler(signal, sender, instance, created, raw, **kwargs):
    if created:
        ct = ContentType.objects.get_for_model(sender)
        assert ViewTracker.objects.filter(content_type=ct, object_id=instance.pk).count() == 0, 'A ViewTracker already existst for %s.' % instance
        v=ViewTracker(content_type=ct, object_id=instance.pk).save()
        logging.debug('%s automatically created for object %s' % (v, instance))

def pre_delete_handler(signal, sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(sender)
    tracker = ViewTracker.objects.filter(content_type=ct, object_id=instance.pk).delete()
    logging.debug('ViewTracker automatically deleted for object %s' % instance)

def register(mymodel):
    assert not issubclass(mymodel, ViewTracker), 'ViewTrackers cannot have ViewTrackers... you fool. Model: %s' % mymodel
    
    post_save.connect(post_save_handler, sender=mymodel)    
    pre_delete.connect(pre_delete_handler, sender=mymodel)

__all__ = ('register', )
