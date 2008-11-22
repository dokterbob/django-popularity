from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class ViewTrackerManager(models.Manager):
    """ Manager methods to do stuff like:
        ViewTracker.objects.get_views_for_model(MyModel) 
    """
    
    def get_views_for_model(self, model):
        return self.get_views_for_models(model)
    
    def get_views_for_models(self, *models):
        """ Returns the objects and its views for a certain model. """
        
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
    
    views = models.PositiveIntegerField()
    
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