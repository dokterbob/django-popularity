from models import ViewTracker

def most_popular(request):
    return {'most_popular' : ViewTracker.objects.get_most_popular() }

def recently_added(request):
    return {'recently_added' : ViewTracker.objects.get_recently_added() }

def recently_viewed(request):
    return {'recently_added' : ViewTracker.objects.get_recently_viewed() }

def most_viewed(request):
    return {'recently_added' : ViewTracker.objects.get_most_viewed() }
