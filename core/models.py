from django.db import models

class Tracker(models.Model):
    last_fetched_subreddit = models.CharField(max_length=30)
    total_fetched_posts = models.IntegerField(default=0)

# Create your models here.
class Subreddit(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class PostLead(models.Model):

    class Status(models.TextChoices):
        NEW = 'New'
        IGNORED = 'Ignored'
        WAITING = 'Waiting'
        REPLIED = 'Replied'
        DM = 'Dm'
        CALL_BOOKED = 'Call booked'
        PROPOSAL_SENT = 'Proposal sent'
        WON = 'Won'
        LOST = 'Lost'


    subreddit = models.ForeignKey(Subreddit, related_name="posts", on_delete=models.CASCADE)
    categorized = models.BooleanField(default=False)
    post_id = models.CharField(max_length=15)
    author_username = models.CharField(max_length=50, null=True, blank=True)
    content = models.TextField()
    number_of_comments = models.IntegerField(default=0)
    url = models.URLField(null=True, blank=True)
    posted_when = models.CharField(max_length=30, null=True, blank=True)
    service_category = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    score = models.IntegerField(default=0)
    estimated_value = models.FloatField(default=0)
    is_good_lead = models.BooleanField(default=False)
    buying_intent = models.CharField(max_length=20, null=True, blank=True)
    urgency = models.CharField(max_length=20, null=True, blank=True)
    competition = models.CharField(max_length=20, null=True, blank=True)
    recommended_action = models.CharField(max_length=20, null=True, blank=True)
    matched_keywords = models.JSONField(null=True, blank=True)
    ai_review = models.TextField()
    suggested_replies = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.subreddit.name} -> {self.post_id}"