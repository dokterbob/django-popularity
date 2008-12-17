import logging

from datetime import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.conf import settings

# Characteristic age, default one hour
# After this amount (in seconds) the novelty is exactly 0.5
CHARAGE = float(getattr(settings, 'CHARAGE', 3600))

_SQL_AGE = '(NOW() - first_view)'
_SQL_MAXVIEWS = '(SELECT MAX(views) FROM %(table)s)'#  % {'table' : db_table }
_SQL_RELVIEWS = '(views/%(maxviews)s)'#  % {'maxviews' : self._SQL_MAXVIEWS }
_SQL_NOVELTY = 'EXP(%(logscaling)s * %(age)s/%(charage)s)'#  % {'logscaling' : logscaling, 'age': self._SQL_AGE, 'charage':CHARAGE }
_SQL_POPULARITY = '%(relviews)s * %(novelty)s'

class ViewTrackerQuerySet(models.query.QuerySet):
    def __init__ (self, model = None, *args, **kwargs):
        super(ViewTrackerQuerySet, self).__init__ (model, *args, **kwargs)
        
        from math import log
        logscaling = log(0.5)
        
        db_table = self.model._meta.db_table
        
        self._SQL_AGE = _SQL_AGE
        self._SQL_MAXVIEWS = _SQL_MAXVIEWS % {'table' : db_table }
        self._SQL_RELVIEWS = _SQL_RELVIEWS % {'maxviews' : self._SQL_MAXVIEWS }
        self._SQL_NOVELTY = _SQL_NOVELTY % {'logscaling' : logscaling, 'age': self._SQL_AGE, 'charage':CHARAGE }
        self._SQL_POPULARITY = _SQL_POPULARITY % {'relviews' : self._SQL_RELVIEWS, 'novelty':self._SQL_NOVELTY }
        
    def select_age(self):
        """ Adds age with regards to NOW to the QuerySet
            fields. """
        assert settings.DATABASE_ENGINE == 'mysql', 'This only works for MySQL.'  
                        
        return self.extra(select={'age': self._SQL_AGE})
        
    def select_relviews(self):
        """ Adds a normalized view count to the QuerySet. """
        return self.extra(select={'relviews': self._SQL_RELVIEWS })

    def select_novelty(self):
        """ Compute novelty. """
        assert settings.DATABASE_ENGINE == 'mysql', 'This only works for MySQL.'
        
        return self.extra(select={'novelty': self._SQL_NOVELTY})
    
    def select_popularity(self):
        """ Compute popularity. """
        assert settings.DATABASE_ENGINE == 'mysql', 'This only works for MySQL.'
        
        return self.extra(select={'popularity' : self._SQL_POPULARITY})
        
    def get_recently_viewed(self, limit=10):
        """ Returns the most recently viewed objects. """
        return self.order_by('-last_view').limit(limit)
    
    def get_for_model(self, model):
        """ Returns the objects and its views for a certain model. """
        return self.get_for_models([model])
    
    def get_for_models(self, models):
        """ Returns the objects and its views for specified models. """

        cts = []
        for model in models:
            cts.append(ContentType.objects.get_for_model(model))
        
        return self.filter(content_type__in=cts)
    
    def get_for_object(self, content_object, create=False):
        """ Gets the viewtracker for specified object, or creates one 
            if requested. """
        
        ct = ContentType.objects.get_for_model(content_object)
        
        if create:
            [viewtracker, created] = self.get_or_create(content_type=ct, object_id=content_object.pk)
        else:
            viewtracker = self.get(content_type=ct, object_id=content_object.pk)
        
        return viewtracker
    
    def get_for_objects(self, objects):
        """ Gets the viewtrackers for specified objects, or creates them 
            if requested. """

        qs = self.none()
        for obj in objects:
            ct = ContentType.objects.get_for_model(obj.__class__)
            
            qs = qs | self.filter(content_type=ct, object_id=obj.pk)
        
        return self & qs

class ViewTrackerManager(models.Manager):
    """ Manager methods to do stuff like:
        ViewTracker.objects.get_views_for_model(MyModel) 
    """
    
    def get_query_set(self):
		return ViewTrackerQuerySet(self.model)
        
    def select_age(self, *args, **kwargs):
        return self.get_query_set().select_age(*args, **kwargs)
        
    def select_relviews(self, *args, **kwargs):
        return self.get_query_set().select_relviews(*args, **kwargs)

    def select_novelty(self, *args, **kwargs):
        return self.get_query_set().select_novelty(*args, **kwargs)
    
    def select_popularity(self, *args, **kwargs):
        return self.get_query_set().select_popularity(*args, **kwargs)
    
    def get_recently_viewed(self, *args, **kwargs):
        return self.get_query_set().get_recently_viewed(*args, **kwargs)
    
    def get_for_model(self, *args, **kwargs):
        return self.get_query_set().get_for_model(*args, **kwargs)
    
    def get_for_models(self, *args, **kwargs):
        return self.get_query_set().get_for_models(*args, **kwargs)
    
    def get_for_object(self, *args, **kwargs):
        return self.get_query_set().get_for_object(*args, **kwargs)
    
    def get_for_objects(self, *args, **kwargs):
        return self.get_query_set().get_for_objects(*args, **kwargs)


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
        ordering = ['-views', '-last_view', 'first_view']
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return u"%s, %d views" % (self.content_object, self.views)
    
    def increment(self):
        """ This increments my view count.
            TODO: optimize in SQL. """
        #logging.debug('Incrementing views for %s from %d to %d' % (self.content_object, self.views, self.views+1))
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
        viewtracker = cls.objects.get_for_object(content_object, create=True)
        
        viewtracker.increment()
        
        return viewtracker
    
    @classmethod
    def get_views_for(cls, content_object):
        """ Gets the total number of views for content_object. """
        ct = ContentType.objects.get_for_model(content_object)
        
        """ If we don't have any views, return 0. """
        try:
            viewtracker = cls.objects.get_for_object(content_object)
        except ViewTracker.DoesNotExist:
            return 0 
        
        return viewtracker.views