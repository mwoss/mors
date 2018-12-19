from django.contrib.auth.models import AbstractUser
from django.forms import ModelForm
from djongo import models
from djongo.models import DjongoManager

from server.mors_seo.managers import MongoUserManager


class SEOResult(models.Model):
    score = models.FloatField()
    query_keywords = models.TextField()
    document_keywords = models.TextField()
    general = models.TextField()
    specific = models.TextField()

    objects = DjongoManager()

    class Meta:
        abstract = True


class SEOResultForm(ModelForm):
    class Meta:
        model = SEOResult
        fields = (
            'score', 'query_keywords', 'document_keywords', 'general', 'specific'
        )


class User(AbstractUser):
    username = models.CharField(unique=True, max_length=30)
    seo_result = models.ArrayModelField(
        model_container=SEOResult,
        model_form_class=SEOResultForm
    )

    objects = MongoUserManager()

    def __str__(self):
        return f'User: {self.username}, email: {self.email}'
