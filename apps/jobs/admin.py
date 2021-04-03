from django.contrib import admin

from .models import Job


class JobAdmin(admin.ModelAdmin):
    date_hierarchy = 'posted_at'

    list_display = ('title', 'location', 'platform')

    list_filter = ['company', 'location', 'platform']

    search_fields = ['title']


admin.site.register(Job, JobAdmin)
