from django.db import models


# Create your models here.
class Job(models.Model):
    title = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    salary = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    project_id = models.TextField(null=True, blank=True)
    contract_type = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    company_avatar = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    min_qualifications = models.TextField(null=True, blank=True)
    preferred_qualifications = models.TextField(null=True, blank=True)
    responsibilities = models.TextField(null=True, blank=True)
    platform = models.TextField()
    active = models.BooleanField(default=False)
    interesting = models.BooleanField(default=False)
    company = models.TextField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-updated_at']
