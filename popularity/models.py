from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from datetime import datetime

class ViewTrackerManager(models.Manager):
    """ Manager methods to do stuff like:
        ViewTracker.objects.get_views_for_model(MyModel) 
    """
    
    def select_age(self, refdate=None):
        """ Adds age with regards to refdate (default: now) to the QuerySet
            fields. """
        if not refdate:
            refdate = datetime.now()
        
        select_string = 'first_view - %s' % refdate
        
        return self.extra(select={'age': select_string})
    
    def get_recently_viewed(self):
        """ Returns the most recently viewed objects. """
        return self.order_by('-last_view')
    
    def get_views_for_model(self, model):
        """ Returns the objects and its views for a certain model. """
        return self.get_views_for_models(model)
    
    def get_views_for_models(self, *models):
        """ Returns the objects and its views for specified models. """
        
        cts = []
        for model in models:
            cts.append(ContentType.objects.get_for_model(model))
        
        return self.filter(content_type__in=cts)

class ViewTracker(models.Model):
    """ The ViewTracker object does exactly what it's supposed to do:
        track the amount of views for an object in order to create make 
        a popularity rating."""
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    first_view = models.DateTimeField(auto_now_add=True)
    last_view = models.DateTimeField(auto_now=True)
    
    views = models.PositiveIntegerField(default=0)
    
    objects = ViewTrackerManager()
    
    class Meta:
        get_latest_by = 'last_view'
        ordering = ['views', '-last_view', 'first_view']
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return u"%s: %d views" % (self.content_object.__unicode__(), self.views)
    
    def increment(self):
        """ This increments my view count.
            TODO: optimize in SQL. """
        self.views = self.views + 1
        self.save()
    
    def get_age(self, refdate=None):
        """ Gets the age of an object relating to a reference date 
            (defaults to now). """
        if not refdate:
            refdate = datetime.now()
        
        assert refdate >= self.first_view, 'Reference date should be equal to or higher than the first view.'
        
        return refdate - self.first_view
    
    @classmethod
    def add_view_for(cls, content_object):
        """ This increments the viewcount for a given object. """
        ct = ContentType.objects.get_for_model(content_object)
        
        viewtracker = cls.objects.get_or_create(content_type=ct, object_id=content_object.id)
        
        viewtracker.increment()
    
    @classmethod
    def get_views_for(cls, content_object):
        """ Gets the total number of views for content_object. """
        ct = ContentType.objects.get_for_model(content_object)
        
        """ If we don't have any views, return 0. """
        try:
            viewtracker = cls.objects.get(content_type=ct, object_id=content_object.id)
        except ViewTracker.DoesNotExist:
            return 0 
        
        return viewtracker.views