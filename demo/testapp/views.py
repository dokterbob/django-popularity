import logging

from django.conf import settings
if 'popularity' in settings.INSTALLED_APPS:
    logging.debug('Django_popularity found and will be used.')
    from popularity.models.ViewTracker import add_view_for
else:
    logging.warn('Django_popularity not found, creating a bogus function.'
    'If popularity does not exist, create a bogus function.'
    def add_view_for(*args, **kwargs):
        pass
