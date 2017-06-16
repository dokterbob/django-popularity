import logging
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.cache import cache
from django.core.validators import validate_ipv46_address

from celery.decorators import task

from popularity.models import ViewTracker

log = logging.getLogger('__name__')


@task
def viewtrack(ct, pk, ip_address):
    '''IP address and caching are for situations where you want
        to not count a page refresh from the same location as another view.
        You can expire it to your specification, 300 (5 minutes) is pretty good though
    '''
    ct = ContentType.objects.get(pk=ct)
    try:
        instance = ct.model_class().objects.get(pk=pk)
    except ct.model_class().DoesNotExist:
        return  # Its gone, deal with it (⌐■_■)

    EXPIRE_TIME = getattr(settings, 'POPULARITY_VIEW_DELAY', 300)
    if EXPIRE_TIME is not False:  # They expicitly don't want any delay
        if "," in ip_address:
            ip_address = ip_address.split(",")[-1].strip()
        validate_ipv46_address(ip_address)
        EXPIRE_KEY = u'popularity-view-%s-%s-%s' % (ct.pk, instance.pk, ip_address)
        log.info(u"%s / %s / %s/ %s" % (EXPIRE_KEY, ct.pk, instance.pk, ip_address))

        if cache.get(EXPIRE_KEY):
            log.info("Foregoing view, recent key found")
            return  # Don't add a view, they're revisiting too soon

        cache.set(EXPIRE_KEY, 1, EXPIRE_TIME)  # 1 == just needs some value

    ViewTracker.add_view_for(instance)
