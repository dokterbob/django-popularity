import unittest

from time import sleep
from models import *
from popularity.models import *


class PopularityTestCase(unittest.TestCase):
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
        for obj in self.objs:
            ViewTracker.add_view_for(obj)
        
        sleep(1)
        
        for obj in self.objs:
            ViewTracker.add_view_for(obj)
        
        viewtrackers = ViewTracker.objects.get_for_objects(self.objs)
        
        for tracker in viewtrackers:
            self.assert_(tracker.last_view > tracker.first_view)
    
    def testAge(self):
        new = TestObject(title='Obj q')
        new.save()
        
        viewtracker = ViewTracker.add_view_for(new)
        first_view = viewtracker.first_view
        
        sleep(1)
        
        ViewTracker.add_view_for(new)
        
        last_view = ViewTracker.objects.get_for_object(new).last_view
                
        from datetime import datetime
        nu = datetime.now()
        
        age = ViewTracker.objects.select_age(refdate=nu).filter(pk=viewtracker.pk)[0].age
        
        self.assertEqual((nu-first_view).seconds, age)

        from django.db import connection
        logging.debug(connection.queries)