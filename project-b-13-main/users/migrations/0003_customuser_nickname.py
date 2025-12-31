from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_customuser_bio_customuser_phone_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='nickname',
            field=models.CharField(
                max_length=50,
                blank=True,
                help_text='Optional nickname/handle displayed instead of your Google name.'
            ),
        ),
    ]