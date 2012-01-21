from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from celery.decorators import task

from popularity.models import ViewTracker

@task
def viewtrack(ct,pk,ip_address):
    '''IP address and caching are for situations where you want
        to not count a page refresh from the same location as another view.
        You can expire it to your specification, 300 (5 minutes) is pretty good though
    '''
    ct = ContentType.objects.get(pk=ct)
    instance = ct.model_class().objects.get(pk=pk)

    EXPIRE_TIME = getattr(settings, 'POPULARITY_VIEW_DELAY', 300)
    if EXPIRE_TIME != False: # They expicitly don't want any delay
        EXPIRE_KEY = 'popularity-view-%s-%s-%s' % (ct.pk, instance.pk, ip_address) 

        if cache.get(EXPIRE_KEY):
            return # Don't add a view, they're revisiting too soon

        cache.set(EXPIRE_KEY, 1, EXPIRE_TIME) # 1 == just needs some value

    ViewTracker.add_view_for(instance)
