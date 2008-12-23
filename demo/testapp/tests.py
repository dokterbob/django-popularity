import unittest

from time import sleep
from models import *
from popularity.models import *

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
                self.assert_(tracker.last_view > tracker.first_view)
    
    def testAge(self):
        from django.conf import settings
        if settings.DATABASE_ENGINE == 'mysql':
            for i in xrange(0,REPEAT_COUNT):
                new = TestObject(title='Obj q')
                new.save()
        
                viewtracker = ViewTracker.add_view_for(new)
                first_view = viewtracker.first_view
        
                sleep(random.randint(1,MAX_SECONDS))
        
                ViewTracker.add_view_for(new)
        
                viewtracker = ViewTracker.add_view_for(new)
                last_view = viewtracker.last_view
                
                calc_age = (datetime.now() - first_view).seconds
        
                age = ViewTracker.objects.select_age().filter(pk=viewtracker.pk)[0].age
        
                db_age = (datetime.now()-first_view).seconds
                
                #try:
                self.assert_(abs(age - db_age) <= 1, "age=%d, db_age=%d" % (age, db_age))
                self.assert_(abs(age - calc_age) <= 1, "age=%d, calc_age=%d" % (age, calc_age))
                self.assertEqual(db_age, calc_age)
                #except:
                #    import ipdb
                #    ipdb.set_trace()
                
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
            first_view = viewtracker.first_view
            
            novelty = ViewTracker.objects.select_novelty(charage=MAX_SECONDS).filter(pk=viewtracker.pk)[0].novelty
            self.assertAlmostEquals(float(novelty), 1.0, 1, 'novelty=%f != 1.0' % novelty)
            
            sleep(MAX_SECONDS)
            
            novelty = ViewTracker.objects.select_novelty(charage=MAX_SECONDS).filter(pk=viewtracker.pk)[0].novelty
            self.assertAlmostEquals(float(novelty), 0.5, 1, 'novelty=%f != 0.5' % novelty)
    
    def testRelage(self):
        from django.conf import settings
        if settings.DATABASE_ENGINE == 'mysql':
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
