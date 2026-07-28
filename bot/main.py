import praw
from prawcore.exceptions import Redirect, NotFound
from .utils import format_timestamp, categorize, save_analyses
from decouple import config as env_config
from core.models import Subreddit, PostLead, Tracker, RedditBotAccount
from django.utils import timezone

# MAKE THE AI TIME AWARE

def fetch_posts_from_subredits():

    account = (
        RedditBotAccount.objects
        .filter(is_active=True)
        .exclude(last_run__date=timezone.localdate())
        .first()
    )

    if not (account.client_id and account.client_secret):
        return "No client ID or secret found for this account"
    
    reddit = praw.Reddit(
        client_id=account.client_id,
        client_secret=account.client_secret,
        user_agent=account.user_agent
    )

    print('-> Initialized praw client')


    subreddits = Subreddit.objects.all().prefetch_related('posts')
    total_fetched = 0

    tracker = Tracker.objects.last()
    
    for subreddit in subreddits:
        print(f'-> Processing {subreddit.name}')
        
        subreddit_name = subreddit.name.removeprefix("r/")

        try:
            print(f'-> Fetching posts for {subreddit.name}')
            submissions = reddit.subreddit(subreddit_name).new(limit=env_config('MAX_POSTS_TO_FETCH', cast=int))
            
            for submission in submissions:
                
                content = submission.selftext
                if not content:
                    continue
                
                print('rerieving--------------------------------------------------')
                post, created = PostLead.objects.get_or_create(
                    post_id=submission.id,
                    subreddit = subreddit
                    )

                # if this lead already exists, skip it
                if not created:
                    continue

                total_fetched += 1

                post.account = account
                post.subreddit = subreddit
                post.author_username = submission.author
                post.content = content
                post.number_of_comments = submission.num_comments
                post.url = submission.url
                post.posted_when = format_timestamp(submission.created_utc)
                post.save()
                
                print(f"-> Saved post with ID: {submission.id} from subreddit: {subreddit.name}")


                tracker.last_fetched_subreddit = subreddit.name

        except (Redirect, NotFound):
            continue

    tracker.total_fetched_posts = total_fetched
    tracker.save()
  
def reset_saved_posts():
   
   PostLead.objects.all().delete()
   
   tracker = Tracker.objects.last()
   tracker.last_fetched_subreddit = ""
   tracker.total_fetched_posts = 0
   tracker.save()

def categorize_posts():

    bot_account = None

    subreddits = Subreddit.objects.all().prefetch_related('posts')
    chuncked_categorize_result = []

    awaiting_categorization = []

    for subreddit in subreddits:
        
        fetch_posts = subreddit.posts.filter(categorized=False)

        print(f'-> Fetched posts: {fetch_posts}\n\n')

        if fetch_posts.count() == 0:
            continue 

        for index, post in enumerate(fetch_posts):
            
            if post.categorized:
                continue

            if bot_account is None:
                bot_account = post.account

            post_summary = {
                "id": post.post_id,
                "content": post.content,
                "posted_when": post.posted_when,
            }

            chuncked_categorize_result.append(post_summary)
            awaiting_categorization.append(post.id)

            if len(chuncked_categorize_result) == 10:
                result = categorize(chuncked_categorize_result)
                analyses = result.get("analyses")

                save_analyses(analyses)

                PostLead.objects.filter(
                    id__in=awaiting_categorization
                ).update(categorized=True)

                chuncked_categorize_result = []
                awaiting_categorization = []
        
            else:
                result = categorize(chuncked_categorize_result)
                analyses = result.get('analyses')
                
                print(f'\n\n-> Saving analusis for result: {analyses}\n\n')
                save_analyses(analyses)
                
                PostLead.objects.filter(
                    id__in=awaiting_categorization
                ).update(categorized=True)

                chuncked_categorize_result = []
                awaiting_categorization = []

    if chuncked_categorize_result:
        result = categorize(chuncked_categorize_result)
        analyses = result.get("analyses")

        save_analyses(analyses)

        PostLead.objects.filter(
            id__in=awaiting_categorization
        ).update(categorized=True)

    bot_account.last_run = timezone.now()
    bot_account.save(update_fields=['last_run'])

    from core.tasks import alert_on_categorization_completion

    alert_on_categorization_completion.delay(
        email=bot_account.categorization_complete_email_recipient.email
    )