from django.db import models

class RequestManager(models.Manager):
    def request_filter(self,request,*args,**kwargs):
        return self.filter(*args,**kwargs)

class UserRequestManager(models.Manager):
    def request_filter(self,request,*args,**kwargs):
        if not 'user' in kwargs:
            kwargs['user'] = request.user
        return self.filter(*args,**kwargs)