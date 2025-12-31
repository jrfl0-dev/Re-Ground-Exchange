from django.apps import AppConfig
import os


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self): #create google environemtn variables

        from django.conf import settings

        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        if not client_id or not client_secret:
            return
        try:
            from django.db import connection
            tables = set(connection.introspection.table_names())
            if not {"django_site", "socialaccount_socialapp"}.issubset(tables):
                return
        except Exception:
            return
        try:
            from django.contrib.sites.models import Site
            from allauth.socialaccount.models import SocialApp,SocialAppSite

            site =Site.objects.get(id=getattr(settings, "SITE_ID", 1))

            app, _=SocialApp.objects.get_or_create(
                provider="google",
                defaults={
                    "name":"Google",
                    "client_id":client_id,
                    "secret":client_secret,
                },
            )
            updated=False
            if app.client_id !=client_id:
                app.client_id=client_id
                updated=True
            if app.secret !=client_secret:
                app.secret=client_secret
                updated=True
            if updated:
                app.save()
            
            SocialAppSite.objects.get_or_create(socialapp=app,site=site)
        except Exception:
            return
        


