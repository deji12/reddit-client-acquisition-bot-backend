from django.contrib import admin
from .models import Tracker, Subreddit, PostLead

class TrackerAdmin(admin.ModelAdmin):
    list_display = ['last_fetched_subreddit', 'total_fetched_posts']

admin.site.register(Tracker, TrackerAdmin)

class SubredditAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Subreddit, SubredditAdmin)

class PostLeadAdmin(admin.ModelAdmin):
    list_display = ['subreddit', 'post_id', 'author_username', 'service_category', 'is_good_lead', 'recommended_action']
    search_fields = ['post_id', 'subreddit__name', 'author_username']
    list_filter = ['subreddit', 'service_category', 'is_good_lead']

admin.site.register(PostLead, PostLeadAdmin)