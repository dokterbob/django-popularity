from django.core.validators import validate_ipv46_address
from django.contrib.contenttypes.models import ContentType

try:
    from popularity.tasks import viewtrack as viewtrack_task
except ImportError:
    viewtrack_task = None  # Celery wasn't found


def viewtrack(request, instance):
    if viewtrack_task is None:
        raise Exception("You must install celery to use this templatetag")
    ''' Like above, except it fires off a task which upticks the views
        (for those that need it super-fast). Also takes into consideration IP address
        to eliminate refresh-duplications
    '''
    ct = ContentType.objects.get_for_model(instance)
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    if len(ip.split(",")) > 1:
        ip = ip.split(",")[-1].strip()
    validate_ipv46_address(ip)
    viewtrack_task.apply_async(args=[ct.pk, instance.pk, ip])
