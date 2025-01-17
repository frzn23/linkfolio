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

class LinkClick(models.Model):
    username = models.CharField(max_length=1000)
    link_type = models.CharField(max_length=100)  # website, instagram, linkedin, youtube
    clicked_at = models.DateTimeField(auto_now_add=True)
    # visitor_ip = models.GenericIPAddressField(null=True)
    
    def __str__(self):
        return f"{self.username} - {self.link_type} click at {self.clicked_at}"