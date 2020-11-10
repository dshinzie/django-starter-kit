from django.db import models
from rest_framework_api_key.models import BaseAPIKeyManager, AbstractAPIKey


class StarterAPIKeyManager(BaseAPIKeyManager):
    def create_key(self, **kwargs):
        kwargs.pop("id", None)
        obj = self.model(**kwargs)
        key = self.assign_key(obj)
        obj.key = key
        obj.save()
        return obj, key
    
    def get_by_natural_key(self, name):
        return self.get(name=name)


class StarterAPIKey(AbstractAPIKey):
    objects = StarterAPIKeyManager()

    key = models.CharField(max_length=41, unique=True, editable=False)
    
    def natural_key(self):
        return (self.name,)
