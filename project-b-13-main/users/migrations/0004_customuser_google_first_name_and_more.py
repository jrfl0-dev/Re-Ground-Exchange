from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customuser_nickname'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='google_first_name',
            field=models.CharField(blank=True, help_text='First name pulled from Google OAuth (read-only).', max_length=50),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='nickname',
            field=models.CharField(blank=True, help_text='Optional nickname/handle displayed instead of Google name or email.', max_length=50),
        ),
    ]
