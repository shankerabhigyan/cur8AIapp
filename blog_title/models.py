from django.db import models
from django.utils import timezone

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class GeneratedTitle(models.Model):
    # blog_post = models.ForeignKey(BlogPost, related_name='generated_titles', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.confidence_score})"

    class Meta:
        ordering = ['-confidence_score']