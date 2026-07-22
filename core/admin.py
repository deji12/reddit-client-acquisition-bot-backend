from django.contrib import admin
from .models import Tracker, Subreddit, PostLead
from import_export.admin import ImportExportModelAdmin

class TrackerAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['last_fetched_subreddit', 'total_fetched_posts']

admin.site.register(Tracker, TrackerAdmin)

class SubredditAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Subreddit, SubredditAdmin)

class PostLeadAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['post_id', 'subreddit', 'service_category', 'is_good_lead', 'recommended_action', 'status', 'posted_when', 'timestamp']
    search_fields = ['post_id', 'subreddit__name', 'author_username']
    list_filter = ['subreddit', 'status', 'service_category', 'is_good_lead', 'timestamp']

admin.site.register(PostLead, PostLeadAdmin)