from django.db import models

# Create your models here.
class Links(models.Model):
    username = models.CharField(max_length=1000)
    website = models.CharField(max_length=1000, null=True, default="")
    insta_url = models.CharField(max_length=1000, null=True, default="")
    linkedin_url = models.CharField(max_length=1000, null=True, default="")
    youtube_url = models.CharField(max_length=1000, null=True, default="")
    theme = models.CharField(max_length=1000, null=True, default="")
    link_status = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username