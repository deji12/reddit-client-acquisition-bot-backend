from celery import shared_task
from bot.main import fetch_posts_from_subredits, categorize_posts
from django.conf import settings
from django.core.mail import EmailMessage

@shared_task
def fetch_and_categorize_posts():

    fetch_posts_from_subredits()
    categorize_posts()


@shared_task
def alert_on_categorization_completion(email):

    email = EmailMessage(
        'Categorization complete',
        'A new categorization has taken place, kindly attend to the posts!\n\nReddit Recruiter.',
        settings.EMAIL_HOST_USER,
        [email]
    )
    email.fail_silently = True
    email.send()