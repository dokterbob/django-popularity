import django.dispatch

from models import ViewTracker

view = django.dispatch.Signal()

def view_handler(signal, sender):
    ViewTracker.add_view_for(sender)

view.connect(view_handler)

# Use this in the following way:
# from popularity.signals import view
# view.send(myinstance)