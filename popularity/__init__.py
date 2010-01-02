import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_delete

from models import ViewTracker

def post_save_handler(signal, sender, instance, created, raw, **kwargs):
    if created:
        ct = ContentType.objects.get_for_model(sender)
        assert ViewTracker.objects.filter(content_type=ct, object_id=instance.pk).count() == 0, 'A ViewTracker already existst for %s.' % instance
        v=ViewTracker(content_type=ct, object_id=instance.pk).save()
        logging.debug('%s automatically created for object %s' % (v, instance))

def pre_delete_handler(signal, sender, instance, **kwargs):
    ct = ContentType.objects.get_for_model(sender)
    tracker = ViewTracker.objects.filter(content_type=ct, object_id=instance.pk)
    assert tracker.count() == 1, 'There are less or more than one ViewTrackers for object %s.' % instance
    tracker.delete()
    logging.debug('ViewTracker automatically deleted for object %s' % instance)

def register(mymodel):
    assert not issubclass(mymodel, ViewTracker), 'ViewTrackers cannot have ViewTrackers... you fool. Model: %s' % mymodel
    
    post_save.connect(post_save_handler, sender=mymodel)    
    pre_delete.connect(pre_delete_handler, sender=mymodel)
    logging.debug('ViewTracker registered for model \'%s\'' % mymodel)

__all__ = ('register', )
