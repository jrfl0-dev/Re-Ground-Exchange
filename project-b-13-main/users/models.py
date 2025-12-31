from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('regular', 'Regular User'),
        ('admin', 'Admin User'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='regular')
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_images = models.ImageField(upload_to='profiles/', blank=True)
    nickname = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional nickname/handle displayed instead of Google name or email."
    )
    google_first_name = models.CharField(max_length=50, blank=True,
                                         help_text="First name pulled from Google OAuth (read-only).")

    def __str__(self):
        return self.email

    def is_admin_user(self):
        return self.user_type == 'admin'
    
    def get_display_name(self):
        # nickname > Google first_name (only if Google account) > email
        nick = (self.nickname or '').strip()
        if nick:
            return nick
        # Only use first_name if this account has an attached Google SocialAccount
        if hasattr(self, 'socialaccount_set') and self.socialaccount_set.filter(provider='google').exists():
            first = (self.first_name or '').strip()
            if first:
                return first
        return (self.email or '').strip()

    def get_average_rating(self):
        from django.db.models import Avg
        # reviews_received is the related_name from Review model
        avg = self.reviews_received.aggregate(Avg('rating'))['rating__avg']
        if avg:
            return round(avg, 1)
        return None

    def get_review_count(self):
        return self.reviews_received.count()