from django.db import models

class CallbackRegistration(models.Model):
    url = models.CharField(max_length=1024)
