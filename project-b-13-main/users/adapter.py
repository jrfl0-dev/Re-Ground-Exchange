from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        first = (data.get("first_name") or "").strip()
        if first:
            user.first_name = first
            if hasattr(user, "google_first_name"):
                user.google_first_name = first
        return user