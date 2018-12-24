#! TODO this was copied from lablackey.db.models, but much was deleted
# Named model, slug model, ordered model, tree model...
# review and decide which to keep

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField

from unrest.managers import RequestManager, UserRequestManager

def as_json(self):
  out = { f: getattr(self,f) for f in self.json_fields }
  for f in self.fk_json_fields:
    if getattr(self,f):
      out[f] = getattr(self,f).as_json
  for f in self.m2m_json_fields:
    out[f] = [i.as_json for i in getattr(self,f)]
  return out

class JsonMixin(object):
  json_fields = []
  filter_fields = []
  m2m_json_fields = []
  fk_json_fields = []
  as_json = property(as_json)

class JsonModel(models.Model,JsonMixin):
  created = models.DateTimeField(auto_now_add=True)
  data_hash = models.BigIntegerField()
  data = JSONField(default=dict)
  objects = RequestManager()

  def save(self,*args,**kwargs):
    if not self.data_hash:
      self.data_hash = hash(json.dumps(self.data,sort_keys=True))
    super().save(*args,**kwargs)

  class Meta:
    abstract = True

class UserModel(JsonModel):
  user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
  objects = UserRequestManager()
  class Meta:
    abstract = True
