import unittest

from time import sleep
from models import *
from popularity.models import *
from popularity import register

import random
from datetime import datetime

REPEAT_COUNT = 3
MAX_SECONDS = 2

class PopularityTestCase(unittest.TestCase):
    def random_view(self):
        ViewTracker.add_view_for(random.choice(self.objs))
        
    def setUp(self):        
        TestObject(title='Obj a').save()
        TestObject(title='Obj b').save()
        TestObject(title='Obj c').save()
        TestObject(title='Obj d').save()
        TestObject(title='Obj e').save()
        TestObject(title='Obj f').save()
        TestObject(title='Obj g').save()
        TestObject(title='Obj h').save()
        TestObject(title='Obj i').save()
        TestObject(title='Obj j').save()
        TestObject(title='Obj k').save()
        TestObject(title='Obj l').save()
        TestObject(title='Obj m').save()
        TestObject(title='Obj n').save()
        
        self.objs = TestObject.objects.all()
    
    def testViews(self):
        views = {}
        for obj in self.objs:
            views.update({obj :ViewTracker.get_views_for(obj)})

        for obj in self.objs:
            ViewTracker.add_view_for(obj)
            self.assertEquals(ViewTracker.get_views_for(obj), views[obj]+1)

        for obj in self.objs:
            ViewTracker.add_view_for(obj)
            self.assertEquals(ViewTracker.get_views_for(obj), views[obj]+2)
    
    def testViewTrackers(self):
        for obj in self.objs:
            ViewTracker.add_view_for(obj)
        
        viewtrackers = ViewTracker.objects.get_for_objects(self.objs)
        
        self.assertEqual(len(viewtrackers), len(self.objs))
    
    def testLastViewed(self):
        for i in xrange(0, REPEAT_COUNT):
            for obj in self.objs:
                ViewTracker.add_view_for(obj)
        
            sleep(random.randint(1,MAX_SECONDS))
        
            for obj in self.objs:
                ViewTracker.add_view_for(obj)
        
            viewtrackers = ViewTracker.objects.get_for_objects(self.objs)
        
            for tracker in viewtrackers:
                self.assert_(tracker.last_view > tracker.added)
    
    def testAge(self):
        from django.conf import settings
        if settings.DATABASE_ENGINE == 'mysql':
            for i in xrange(0,REPEAT_COUNT):
                new = TestObject(title='Obj q')
                new.save()
                
                # This sets the first view for our test object
                viewtracker = ViewTracker.add_view_for(new)
                
                # Note down the initial time
                # Request the initial time from the database
                old_time = datetime.now()
                added = viewtracker.added
                
                #import ipdb; ipdb.set_trace()
                
                # These should be the same with at most a 1 second difference
                self.assert_(abs((old_time-added).seconds) <= 1, "old_time=%s, added=%s" % (old_time, added))
                
                # Wait a random number of seconds
                wait = random.randint(1,MAX_SECONDS)
                sleep(wait)
                
                # This sets the last view for the same object
                viewtracker = ViewTracker.add_view_for(new)
                
                # Do the same checks
                new_time = datetime.now()
                last_view = viewtracker.last_view
                
                # These should be the same with at most a 1 second difference
                self.assert_(abs((new_time-last_view).seconds) <= 1, "new_time=%s, last_view=%s" % (new_time, last_view))
                                
                # Now see if we have calculated the age right, using previous queries
                calc_age = (new_time - old_time).seconds
                db_age = (last_view - added).seconds
                self.assert_(abs(db_age - calc_age) <= 1, "db_age=%d, calc_age=%d" % (db_age, calc_age))
                
                # Check if we indeed waited the righ amount of time 'test the test'
                self.assert_(abs(wait - calc_age) <= 1, "wait=%d, calc_age=%d" % (wait, calc_age))
                
                # Now rqeuest the age from the QuerySet
                age = ViewTracker.objects.select_age().filter(pk=viewtracker.pk)[0].age
                
                # See whether it matches
                self.assert_(abs(age - db_age) <= 1, "age=%d, db_age=%d" % (age, db_age))
                self.assert_(abs(age - calc_age) <= 1, "age=%d, calc_age=%d" % (age, calc_age))    
            
            # Just a retarded test to see if we have no negative ages for objects    
            for o in ViewTracker.objects.select_age():
                self.assert_(o.age >= 0, "Negative age %f for object <%s>." % (o.age, o))
                    
    
    def testRelviews(self):
        from django.conf import settings
        if settings.DATABASE_ENGINE == 'mysql':
            for i in xrange(0,REPEAT_COUNT):
                self.random_view()
                
                maxviews = 0
            
                for obj in ViewTracker.objects.all():
                    if obj.views > maxviews:
                        maxviews = obj.views
            
                for obj in ViewTracker.objects.select_relviews():
                    relviews_expected = float(obj.views)/maxviews
                    self.assertAlmostEquals(float(obj.relviews), relviews_expected, 3, 'views=%d, relviews=%f, expected=%f' % (obj.views, obj.relviews, relviews_expected))
    
    def testNovelty(self):
        from django.conf import settings
        if settings.DATABASE_ENGINE == 'mysql':
            new = TestObject(title='Obj q')
            new.save()
            
            viewtracker = ViewTracker.add_view_for(new)
            added = viewtracker.added
            
            novelty = ViewTracker.objects.select_novelty(charage=MAX_SECONDS).filter(pk=viewtracker.pk)[0].novelty
            self.assertAlmostEquals(float(novelty), 1.0, 1, 'novelty=%f != 1.0' % novelty)
            
            sleep(MAX_SECONDS)
            
            novelty = ViewTracker.objects.select_novelty(charage=MAX_SECONDS).filter(pk=viewtracker.pk)[0].novelty
            self.assertAlmostEquals(float(novelty), 0.5, 1, 'novelty=%f != 0.5' % novelty)
    
    def testRelage(self):
        from django.conf import settings
        if settings.DATABASE_ENGINE == 'mysql':
            for x in xrange(REPEAT_COUNT):
                new = TestObject(title='Obj q')
                new.save()
    
                viewtracker = ViewTracker.add_view_for(new)
            
                relage = ViewTracker.objects.select_relage()
                youngest = relage.order_by('relage')[0]
            
                self.assertEqual(viewtracker, youngest)
                self.assertAlmostEquals(float(youngest.relage), 0.0, 2)
            
                oldest_age = ViewTracker.objects.select_age().order_by('-age')[0]
                oldest_relage = relage.order_by('-relage')[0]
            
                self.assertEqual(oldest_relage, oldest_age)
                self.assertAlmostEquals(float(oldest_relage.relage), 1.0, 2)
                
                sleep(MAX_SECONDS)
