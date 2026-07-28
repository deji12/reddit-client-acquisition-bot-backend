from django.db import models

class EmailForNotification(models.Model):
    email = models.EmailField(
        help_text=(
            "The email to be notified when post fetching and categorization is complete"
        )
    )

    def __str__(self):
        return self.email

class RedditBotAccount(models.Model):

    categorization_complete_email_recipient = models.ForeignKey(
        EmailForNotification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=(
            "The email address that will be notified when the AI has finished fetching and categorizing posts"
        )
    )

    client_id = models.CharField(
        max_length=100,
        help_text=(
            "The client ID of this account gotten from https://www.reddit.com/prefs/apps "
        )
    )
    client_secret = models.CharField(
        max_length=150,
        help_text=(
            "The client secret of this account gotten from https://www.reddit.com/prefs/apps "
        )
    )
    user_agent = models.CharField(
        max_length=20,
        help_text=(
            "The user agent of this account"
        ),
        default=""
    )
    is_active = models.BooleanField(
        default=False,
        help_text=(
            "This activates or deactivates a bot account "
        )
    )
    last_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When last this bot account ran"
    )

    def __str__(self):
        return self.client_id


class Tracker(models.Model):
    last_fetched_subreddit = models.CharField(
        max_length=30,
        blank=True,
        default="",
        help_text=(
            "The most recent subreddit processed by the Reddit post-fetching task."
        ),
    )

    total_fetched_posts = models.IntegerField(
        default=0,
        help_text=(
            "The total number of new Reddit posts saved during the latest fetch."
        ),
    )

    def __str__(self):
        return f"Tracker - {self.total_fetched_posts} posts"


class Subreddit(models.Model):

    name = models.CharField(
        max_length=50,
        help_text=(
            "The subreddit to monitor. You may enter it as 'webdev' or 'r/webdev'."
        ),
    )

    def __str__(self):
        return self.name


class PostLead(models.Model):

    class Status(models.TextChoices):
        NEW = "New", "New"
        IGNORED = "Ignored", "Ignored"
        WAITING = "Waiting", "Waiting"
        REPLIED = "Replied", "Replied"
        DM = "Dm", "DM sent"
        CALL_BOOKED = "Call booked", "Call booked"
        PROPOSAL_SENT = "Proposal sent", "Proposal sent"
        WON = "Won", "Won"
        LOST = "Lost", "Lost"

    account = models.ForeignKey(
        RedditBotAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=(
            "The bot account that fetched this post lead"
        ) 
    )

    subreddit = models.ForeignKey(
        Subreddit,
        related_name="posts",
        on_delete=models.CASCADE,
        help_text="The subreddit where this post was discovered.",
    )

    categorized = models.BooleanField(
        default=False,
        help_text=(
            "Indicates whether this post has already been analyzed and categorized "
            "by the AI."
        ),
    )

    post_id = models.CharField(
        max_length=15,
        help_text="The unique Reddit ID assigned to this post.",
    )

    author_username = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=(
            "The Reddit username of the post author. This may be empty if the "
            "account was deleted."
        ),
    )

    content = models.TextField(
        help_text="The main text content of the Reddit post.",
    )

    number_of_comments = models.IntegerField(
        default=0,
        help_text=(
            "The number of comments the Reddit post had when it was last fetched."
        ),
    )

    url = models.URLField(
        null=True,
        blank=True,
        help_text="The direct URL to the original Reddit post.",
    )

    posted_when = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text=(
            "A readable version of the date and time when the post was published."
        ),
    )

    service_category = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text=(
            "The service category assigned by the AI, such as website, Shopify, "
            "bot, automation, chatbot, or other."
        ),
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        help_text=(
            "The current sales pipeline stage for this lead, from New through "
            "Won or Lost."
        ),
    )

    score = models.IntegerField(
        default=0,
        help_text=(
            "The AI-generated lead quality score from 0 to 100. Higher scores "
            "indicate stronger commercial opportunities."
        ),
    )

    estimated_value = models.FloatField(
        default=0,
        help_text=(
            "The AI-estimated potential project value in US dollars."
        ),
    )

    is_good_lead = models.BooleanField(
        default=False,
        help_text=(
            "Indicates whether the AI considers this post a worthwhile sales lead."
        ),
    )

    buying_intent = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text=(
            "The estimated likelihood that the author intends to hire or purchase "
            "a service, such as high, medium, low, or none."
        ),
    )

    urgency = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text=(
            "The estimated urgency of the author's request, such as high, medium, "
            "low, or none."
        ),
    )

    competition = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text=(
            "The estimated level of competition from other developers or agencies "
            "responding to the post."
        ),
    )

    recommended_action = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text=(
            "The AI-recommended next step for this lead, such as reply, watch, "
            "or ignore."
        ),
    )

    matched_keywords = models.JSONField(
        null=True,
        blank=True,
        help_text=(
            "A list of relevant words or phrases found in the post that influenced "
            "the AI analysis."
        ),
    )

    ai_review = models.TextField(
        blank=True,
        default="",
        help_text=(
            "A concise AI-generated explanation of the lead quality, business fit, "
            "buying intent, urgency, and competition."
        ),
    )

    suggested_replies = models.JSONField(
        null=True,
        blank=True,
        help_text=(
            "AI-generated Reddit reply suggestions tailored to the content of "
            "this post."
        ),
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        help_text="The date and time when this lead was first saved.",
    )

    def __str__(self):
        return f"{self.subreddit.name} -> {self.post_id}"