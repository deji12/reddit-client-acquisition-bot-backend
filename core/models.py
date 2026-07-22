from django.db import models

class Tracker(models.Model):
    last_fetched_subreddit = models.CharField(max_length=30)
    total_fetched_posts = models.IntegerField(default=0)

# Create your models here.
class Subreddit(models.Model):
    name = models.CharField(max_length=50)
    
class PostLead(models.Model):
    subreddit = models.ForeignKey(Subreddit, on_delete=models.CASCADE)
    post_id = models.CharField(max_length=15)
    author_username = models.CharField(max_length=50)
    content = models.TextField()
    url = models.URLField()
    service_category = models.CharField(max_length=20)
    score = models.IntegerField()
    estimated_value = models.FloatField(default=0)
    is_good_lead = models.BooleanField(default=False)
    buying_intent = models.CharField(max_length=20)
    urgency = models.CharField(max_length=20)
    competition = models.CharField(max_length=20)
    recommended_action = models.CharField(max_length=20)
    matched_keywords = models.JSONField()
    ai_review = models.TextField()
    suggested_replies = models.JSONField()

    def __str__(self):
        return f"{self.subreddit.name} -> {self.post_id}"