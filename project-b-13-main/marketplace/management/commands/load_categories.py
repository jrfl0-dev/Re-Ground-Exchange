from django.core.management.base import BaseCommand
from marketplace.models import Category

class Command(BaseCommand):
    help = 'Load initial categories for the marketplace'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Furniture', 'description': 'Desks, chairs, beds, and more', 'icon': '🛋️'},
            {'name': 'Electronics', 'description': 'Laptops, phones, accessories', 'icon': '💻'},
            {'name': 'Textbooks', 'description': 'Course books and study materials', 'icon': '📚'},
            {'name': 'Kitchenware', 'description': 'Pots, pans, utensils', 'icon': '🍳'},
            {'name': 'Clothing', 'description': 'Clothes and accessories', 'icon': '👕'},
            {'name': 'Sports Equipment', 'description': 'Fitness gear and sports items', 'icon': '⚽'},
            {'name': 'Decor', 'description': 'Room decoration items', 'icon': '🎨'},
            {'name': 'School Supplies', 'description': 'Notebooks, pens, and more', 'icon': '✏️'},
        ]

        for cat_data in categories:
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon']
                }
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully loaded categories')
        )