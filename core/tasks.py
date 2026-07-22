from celery import shared_task
from bot.main import fetch_posts_from_subredits, categorize_posts

@shared_task
def fetch_new_posts():
    fetch_posts_from_subredits()

@shared_task
def categorize_fetched_posts():
    categorize_posts()