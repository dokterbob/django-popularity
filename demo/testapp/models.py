from django.db import models

class TestObject(models.Model):
    title = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.title