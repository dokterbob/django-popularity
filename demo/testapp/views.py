from django.conf import settings
if 'popularity' in settings.INSTALLED_APPS:
    POPULARITY = True
    from popularity.models.ViewTracker import add_view_for
else:
    POPULARITY = False
