from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

from users.models import ProgrammingLanguage

class Problem(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='problems')
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.SET_NULL, related_name='problems', null=True, blank=True)

    def __str__(self):
        return self.title
    
    
    