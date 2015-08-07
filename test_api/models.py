from django.db import models

class LastMessage(models.Model):
    text = models.TextField()

    @staticmethod
    def get_only():
        m_list = LastMessage.objects.all()[:1]
        if len(m_list) > 0:
            return m_list[0]
        else:
            m = LastMessage(text='')
            m.save()
            return m

class CallbackRegistration(models.Model):
    url = models.CharField(max_length=1024)
