from djongo import models


class Site(models.Model):
    url = models.URLField()
    tittle = models.CharField(max_length=100)
    description = models.TextField()

    objects = models.DjongoManager()
