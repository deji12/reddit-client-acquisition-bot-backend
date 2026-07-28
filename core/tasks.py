from celery import shared_task
from bot.main import fetch_posts_from_subredits, categorize_posts

@shared_task
def fetch_and_categorize_posts():
    
    fetch_posts_from_subredits()
    categorize_posts()